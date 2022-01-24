from odoo import api, fields, models, _


class AxxStockQuantInherited(models.Model):
    _inherit = "stock.quant"

    axx_length = fields.Integer(string='Length')
    axx_width = fields.Integer(string='Width')
    axx_height = fields.Integer(string='Height')
    axx_pallet_id = fields.Many2one(comodel_name='axx.stock.pallet', string='Pallet')

    def action_store_products(self):
        '''
        To open a wizard which gives the option to select the location to
        which the user want to store the product
        '''
        wizard_view_id = self.env.ref('axx_stock_extensions.view_axx_stock_product_wizard')
        return {
            'name': _('Store Products'),
            'view_mode': 'form',
            'view_id': wizard_view_id.id,
            'res_model': 'axx.store.product',
            'domain': [],
            'context': dict(self._context, active_ids=self.ids),
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_retrieve_products(self):
        '''
        To open a wizard which gives the option to select the production location to
        which the user want to retrieve the product
        '''
        wizard_view_id = self.env.ref('axx_stock_extensions.view_axx_retrieve_product_wizard')
        return {
            'name': _('Retrieve Products'),
            'view_mode': 'form',
            'view_id': wizard_view_id.id,
            'res_model': 'axx.store.product',
            'domain': [],
            'context': dict(self._context, active_ids=self.ids),
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
