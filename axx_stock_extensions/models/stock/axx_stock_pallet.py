from odoo import api, fields, models, _


class AxxStockPallet(models.Model):
    _name = 'axx.stock.pallet'
    _description = 'Pallet associated with location'

    name = fields.Char(string='Pallet', required=True, copy=False,
                       default=lambda self: self.env['ir.sequence'].next_by_code('axx.stock.pallet') or _('New'))
    axx_location_id = fields.Many2one(comodel_name='stock.location', string='Location', ondelete='set null')
