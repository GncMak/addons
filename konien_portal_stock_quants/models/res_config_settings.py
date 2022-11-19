from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    quants_domain = fields.Char('Domain for Quants', default='[]')
    incoming_domain = fields.Char('Domain for Incoming', default='[]')

    quants_show = fields.Boolean('Show Quants', default=False)
    incoming_show = fields.Boolean('Show Incoming', default=False)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            {
                'quants_domain': self.env['ir.config_parameter'].sudo().get_param('konien_portal_stock_quants.quants_domain'),
                'incoming_domain': self.env['ir.config_parameter'].sudo().get_param('konien_portal_stock_quants.incoming_domain'),
                'quants_show': self.env['ir.config_parameter'].sudo().get_param('konien_portal_stock_quants.quants_show'),
                'incoming_show': self.env['ir.config_parameter'].sudo().get_param('konien_portal_stock_quants.incoming_show'),
            }
        )
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('konien_portal_stock_quants.quants_domain', self.quants_domain)
        self.env['ir.config_parameter'].sudo().set_param('konien_portal_stock_quants.incoming_domain', self.incoming_domain)

        self.env['ir.config_parameter'].sudo().set_param('konien_portal_stock_quants.quants_show', self.quants_show)
        self.env['ir.config_parameter'].sudo().set_param('konien_portal_stock_quants.incoming_show', self.incoming_show)
        return res
