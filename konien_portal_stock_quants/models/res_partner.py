from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    visible_quants_portal = fields.Boolean('Show Quantities On Portal', default=False)
