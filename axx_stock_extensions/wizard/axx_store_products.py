from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AxxStoreProduct(models.TransientModel):
    _name = "axx.store.product"
    _description = "Store products in location"

    def _axx_default_note_values(self):
        """
        To list the location(s) already having the selected products and empty locations
        """
        quant_ids = self.env['stock.quant'].browse(self.env.context.get('active_ids'))
        notes = ''
        for quant_id in quant_ids:
            location_ids = self.env['stock.quant'].search([
                ('product_id', '=', quant_id.product_id.id), ('location_id.usage', '=', 'internal'),
                ('location_id.axx_is_production_loc', '=', False)]).mapped('location_id')
            for location_id in location_ids:
                qty = quant_id.product_id.with_context(location=location_id.id).virtual_available
                notes += '%s is in location %s having quantity %s\n' %\
                         (quant_id.product_id.name, location_id.display_name, int(qty))
        return notes

    def _axx_default_field_values(self):
        """
        Bring the selected product details
        """
        quant_ids = self.env['stock.quant'].browse(self.env.context.get('active_ids'))
        store_lines = []
        for quant_id in quant_ids:
            store_lines.append((0, 0,
                                {'axx_quant_id': quant_id.id,
                                 'axx_product_id': quant_id.product_id.id,
                                 'axx_available_qty':
                                    quant_id.product_id.with_context(location=quant_id.location_id.id).virtual_available,
                                 'axx_length': quant_id.axx_length,
                                 'axx_width': quant_id.axx_width,
                                 'axx_height': quant_id.axx_height,
                                 'axx_pallet_id': quant_id.axx_pallet_id and quant_id.axx_pallet_id.id,
                                 }))
        return store_lines

    axx_store_line_ids = fields.One2many(comodel_name='axx.store.product.line', inverse_name='axx_store_wiz_id',
                                         string='Store Wizard', default=_axx_default_field_values)
    axx_note = fields.Text(string='Notes', default=_axx_default_note_values)
    axx_is_pallet_received = fields.Boolean(string='Is Pallet Received')

    def axx_get_pallet_notification(self):
        """
        Trigger call to the microservice to get the pallet
        """
        for record in self:
            record.axx_is_pallet_received = True
        message = "Pallet requested"
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'warning',
                'message': _(message),
            }
        }

    def axx_make_transfer(self):
        """
        To move the pallet from receiving location to the actual storing internal location
        """
        if not self.axx_is_pallet_received:
            raise UserError(_('Pallet required for transfer. Please collect the pallet first'))
        transit_loc_id = self.env['stock.location'].search([('usage', '=', 'transit')], limit=1)
        if not transit_loc_id:
            raise UserError(_('No transit location exists. Please create one!'))
        for line_id in self.axx_store_line_ids:
            if line_id.axx_quantity_to_move > line_id.axx_available_qty:
                raise UserError(_('Make sure the entered quantity is available before transfer'))
            if line_id.axx_quantity_to_move != line_id.axx_available_qty:
                if line_id.axx_quantity_to_move < line_id.axx_available_qty:
                    line_id.axx_quant_id.quantity -= line_id.axx_quantity_to_move
                    self.env['stock.quant'].create({'product_id': line_id.axx_product_id.id,
                                                    'location_id': transit_loc_id and transit_loc_id.id or False,
                                                    'quantity': line_id.axx_quantity_to_move,
                                                    'axx_length': line_id.axx_length,
                                                    'axx_width': line_id.axx_width,
                                                    'axx_height': line_id.axx_height,
                                                    'axx_pallet_id': line_id.axx_pallet_id and line_id.axx_pallet_id.id
                                                    or False})
                    self.env['axx.stock.pallet.log'].create({'name': line_id.axx_pallet_id.id,
                                                             'axx_product_id': line_id.axx_product_id.id,
                                                             'axx_location_id': line_id.axx_quant_id.location_id.id,
                                                             'axx_location_dest_id': transit_loc_id and transit_loc_id.id
                                                             or False,
                                                             'axx_quantity': line_id.axx_quantity_to_move,
                                                             'axx_user_id': self.env.user.id})
            else:
                self.env['axx.stock.pallet.log'].create({'name': line_id.axx_pallet_id.id,
                                                         'axx_product_id': line_id.axx_product_id.id,
                                                         'axx_location_id': line_id.axx_quant_id.location_id.id,
                                                         'axx_location_dest_id': transit_loc_id and transit_loc_id.id
                                                         or False,
                                                         'axx_quantity': line_id.axx_quantity_to_move,
                                                         'axx_user_id': self.env.user.id})
                line_id.axx_quant_id.write({'location_id': transit_loc_id and transit_loc_id.id
                                            or False, 'axx_length': line_id.axx_length,
                                            'axx_width': line_id.axx_width, 'axx_height': line_id.axx_height,
                                            'axx_pallet_id': line_id.axx_pallet_id and line_id.axx_pallet_id.id or False})


class AxxStoreProductLines(models.TransientModel):
    _name = "axx.store.product.line"
    _description = "Store products lines"

    def get_location_domain(self):
        """
        To get the empty locations and locations in which the product already available.
        """
        ctx = dict(self.env.context)
        quant_ids = self.env['stock.quant'].browse(ctx.get('active_ids', []))
        location_obj = self.env['stock.location']
        quant_obj = self.env['stock.quant']
        for quant_id in quant_ids:
            if quant_id.product_id:
                location_ids = location_obj.search([('usage', '=', 'internal'), ('axx_is_production_loc', '=', False)])
                stock_quant_ids = quant_obj.search([('location_id', 'in', location_ids.ids),
                                                    ('product_id', '=', quant_id.product_id.id),
                                                    ('location_id.usage', '=', 'internal'),
                                                    ('axx_length', '=', quant_id.axx_length),
                                                    ('axx_width', '=', quant_id.axx_width),
                                                    ('axx_height', '=', quant_id.axx_height)])
                product_location_ids = stock_quant_ids and stock_quant_ids.mapped('location_id')
                other_non_empty_loc_ids = quant_obj.search([('location_id', '=', location_ids.ids),
                                                            ('location_id.usage', '=', 'internal'),
                                                            ('location_id.axx_is_production_loc', '=', False),
                                                            ('product_id', '!=', quant_id.product_id.id)])
                non_empty_location_list = product_location_ids and product_location_ids.ids or []
                non_empty_location_list += other_non_empty_loc_ids and other_non_empty_loc_ids.ids
                empty_location_ids = location_obj.search([('id', 'not in', non_empty_location_list)])
                location_domain = product_location_ids and product_location_ids.ids or []
                location_domain += empty_location_ids and empty_location_ids.ids
                return [('usage', '=', 'internal'), ('id', 'in', location_domain),
                        ('axx_is_production_loc', '=', False), ('axx_is_goods_receipt_loc', '=', False)]

    axx_store_wiz_id = fields.Many2one(comodel_name='axx.store.product', ondelete='set null')
    axx_quant_id = fields.Many2one(comodel_name='stock.quant', string='Quant')
    axx_product_id = fields.Many2one(comodel_name='product.product', string='Product')
    axx_location_id = fields.Many2one(comodel_name='stock.location', string='Location',
                                      domain=lambda self: self.get_location_domain())
    axx_pallet_id = fields.Many2one(comodel_name='axx.stock.pallet', string='Pallet')
    axx_available_qty = fields.Float(string='Available Qty')
    axx_quantity_to_move = fields.Float(string='Quantity To Move')
    lot_id = fields.Many2one(comodel_name='stock.production.lot', string='Lot #')
    axx_length = fields.Float(string='Length')
    axx_width = fields.Float(string='Width')
    axx_height = fields.Float(string='Height')

    @api.onchange('axx_product_id')
    def axx_onchange_product(self):
        """
        To get the empty locations and locations in which the product already available.
        """
        for record in self:
            if record.axx_product_id:
                location_ids = self.env['stock.location'].search([('usage', '=', 'internal'),
                                                                  ('axx_is_production_loc', '=', False)])
                quant_ids = self.env['stock.quant'].search([('location_id', 'in', location_ids.ids),
                                                            ('product_id', '=', record.axx_product_id.id),
                                                            ('location_id.usage', '=', 'internal')])
                product_location_ids = quant_ids and quant_ids.mapped('location_id')
                other_non_empty_loc_ids = self.env['stock.quant'].search([('location_id', 'in', location_ids.ids),
                                                                          ('location_id.usage', '=', 'internal'),
                                                                          ('location_id.axx_is_production_loc', '=', False),
                                                                          ('product_id', '!=', record.axx_product_id.id)])
                non_empty_location_list = product_location_ids and product_location_ids.ids
                non_empty_location_list += other_non_empty_loc_ids and other_non_empty_loc_ids.ids
                empty_location_ids = self.env['stock.location'].search([('id', 'not in', non_empty_location_list),
                                                                        ('axx_is_production_loc', '=', False)])
                location_domain = product_location_ids and product_location_ids.ids
                location_domain += empty_location_ids and empty_location_ids.ids
                return {'domain': {'axx_location_id': [('usage', '=', 'internal'), ('id', 'in', location_domain)]}}

    @api.onchange('axx_location_id')
    def axx_onchange_location(self):
        """
        To get the pallet information associated with the location
        """
        for line_id in self:
            if line_id.axx_location_id:
                line_id.axx_pallet_id = line_id.axx_location_id.axx_pallet_id and line_id.axx_location_id.axx_pallet_id.id or False
