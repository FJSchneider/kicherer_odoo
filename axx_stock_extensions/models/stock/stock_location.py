from odoo import api, fields, models, _


class AxxStockLocationInherited(models.Model):
    _inherit = 'stock.location'

    axx_is_goods_receipt_loc = fields.Boolean(string='Is Goods receipt Location')
    axx_pallet_count = fields.Selection([('zero', 'Empty'), ('one', 'One'), ('two', 'Two')], string='Pallet Count')
    axx_is_production_loc = fields.Boolean(string='Is Production Location')
    axx_pallet_id = fields.Many2one(comodel_name='axx.stock.pallet', string='Pallet')
    axx_loc_height_count = fields.Selection([('zero', 'Empty'), ('one', 'One'), ('two', 'Two')], string='Height Count')
