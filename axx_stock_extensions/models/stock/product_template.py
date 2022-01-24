from odoo import api, fields, models, _


class AxxProductTemplateInherited(models.Model):
    _inherit = "product.template"

    tracking = fields.Selection(selection_add=[('dimension', 'Dimension')], ondelete={'dimension': 'set default'})
