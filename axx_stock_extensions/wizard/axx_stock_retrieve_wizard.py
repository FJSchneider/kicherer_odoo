from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AxxStoreProduct(models.TransientModel):
    _inherit = "axx.store.product"

    axx_is_retrieval_pallet_received = fields.Boolean(string='Is Retrieval Pallet Received')

    def axx_get_retrieval_pallet(self):
        """
        Trigger call to the microservice to get the pallet
        """
        for record in self:
            record.axx_is_retrieval_pallet_received = True
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'warning',
                'message': _("Pallet requested"),
            }
        }

    def axx_make_retrieval_transfer(self):
        """
        Gets the pallet from internal location to the production location
        """
        if not self.axx_is_retrieval_pallet_received:
            raise UserError(_('Pallet required for transfer. Please collect the pallet first'))
        for line_id in self.axx_store_line_ids:
            self.env['axx.stock.pallet.log'].create({'name': line_id.axx_pallet_id.id,
                                                     'axx_product_id': line_id.axx_product_id.id,
                                                     'axx_location_id': line_id.axx_quant_id.location_id.id,
                                                     'axx_location_dest_id': line_id.axx_retrieve_location_id.id,
                                                     'axx_quantity': line_id.axx_quantity_to_move,
                                                     'axx_user_id': self.env.user.id})
            line_id.axx_quant_id.write({'location_id': line_id.axx_retrieve_location_id.id,
                                        'axx_length': line_id.axx_length,
                                        'axx_width': line_id.axx_width, 'axx_height': line_id.axx_height})


class AxxStoreProductLines(models.TransientModel):
    _inherit = "axx.store.product.line"

    def get_retrieve_location_domain(self):
        """
        To get the production locations.
        """
        return [('axx_is_production_loc', '=', True)]

    axx_retrieve_location_id = fields.Many2one(comodel_name='stock.location', string='Retrieve Location',
                                               domain=lambda self: self.get_retrieve_location_domain())

    @api.onchange('axx_retrieve_location_id')
    def onchange_axx_retrieve_location_id(self):
        """
        To get the pallet information associated with the location
        """
        for line_id in self:
            if line_id.axx_retrieve_location_id:
                line_id.axx_pallet_id = line_id.axx_retrieve_location_id.axx_pallet_id and\
                                        line_id.axx_retrieve_location_id.axx_pallet_id.id or False
