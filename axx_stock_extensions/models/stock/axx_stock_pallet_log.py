from odoo import api, fields, models, _


class AxxStockPalletLog(models.Model):
    _name = 'axx.stock.pallet.log'
    _description = 'Stock pallet log for tracking the movement'

    name = fields.Many2one(comodel_name='axx.stock.pallet', string='Pallet')
    axx_date_transfer = fields.Datetime(string='Date of transfer', default=fields.Datetime.now())
    axx_product_id = fields.Many2one(comodel_name='product.product', string='Product')
    axx_location_id = fields.Many2one(comodel_name='stock.location', string='Source')
    axx_location_dest_id = fields.Many2one(comodel_name='stock.location', string='Destination')
    axx_quantity = fields.Float(string='Quantity')
    axx_user_id = fields.Many2one(comodel_name='res.users', string='Responsible')
