from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
from werkzeug.utils import redirect


class PortalProduct(CustomerPortal):

    @http.route('/my/product/<int:product_id>', type='http', auth="user", website=True)
    def index_product(self, product_id, **kw):

        show_incoming = request.env['ir.config_parameter'].sudo().get_param('konien_portal_stock_quants.incoming_show',
                                                                            default=False)
        show_quants = request.env['ir.config_parameter'].sudo().get_param('konien_portal_stock_quants.quants_show',
                                                                            default=False)

        if not request.env.user.partner_id.visible_quants_portal or (not show_incoming and not show_quants):
            return redirect('/my')

        try:
            product = request.env['product.product'].sudo().browse(product_id)
            if not product:
                return redirect('/my')

            values = {
                'product': product,
            }

            return request.render("konien_portal_stock_quants.portal_my_product", values)
        except Exception as e:
            return _(str(e))
