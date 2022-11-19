from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from odoo.tools.safe_eval import safe_eval
from odoo.osv.expression import OR
from werkzeug.utils import redirect


class PortalStockQuant(CustomerPortal):

    def domain_prepare(self, domain):
        if domain == False or domain == []:
            return []
        return safe_eval(domain)

    def _prepare_portal_layout_values(self):
        values = super(PortalStockQuant, self)._prepare_portal_layout_values()
        show_quants = request.env['ir.config_parameter'].sudo().get_param('konien_portal_stock_quants.quants_show',
                                                                            default=False)

        if not request.env.user.partner_id.visible_quants_portal or not show_quants:
            return values

        domain = request.env['ir.config_parameter'].sudo().get_param('konien_portal_stock_quants.quants_domain',
                                                                     default='[]')
        domain = self.domain_prepare(domain)
        quant_count = request.env['stock.quant'].search_count(domain)

        values['quant_count'] = quant_count
        return values

    @http.route(['/my/quants', '/my/quants/page/<int:page>'], type='http', auth="user", website=True)
    def index_quant(self, page=1, search=None, search_in='content', **kw):
        try:
            show_quants = request.env['ir.config_parameter'].sudo().get_param('konien_portal_stock_quants.quants_show',
                                                                                default=False)
            if not request.env.user.partner_id.visible_quants_portal or not show_quants:
                return redirect('/my')

            StockQuant = request.env['stock.quant']
            values = self._prepare_portal_layout_values()
            domain = request.env['ir.config_parameter'].sudo().get_param('konien_portal_stock_quants.quants_domain',
                                                                         default='[]')

            searchbar_inputs = {
                'default_code': {'input': 'default_code',
                                 'label': _('Search <span class="nolabel"> (in Default Code)</span>')},
                'name': {'input': 'name', 'label': _('Search in Product Name')},
                'lot_id': {'input': 'lot_id', 'label': _('Search in Product Lot Id')},
                'all': {'input': 'all', 'label': _('Search in All')},
            }

            domain = self.domain_prepare(domain)

            # search
            if search and search_in:
                search_domain = []
                if search_in in ('default_code', 'all'):
                    search_domain = OR([search_domain, [('product_tmpl_id', 'ilike', search)]])
                if search_in in ('name', 'all'):
                    search_domain = OR([search_domain, [('product_tmpl_id', 'ilike', search)]])
                if search_in in ('lot_id', 'all'):
                    search_domain = OR([search_domain, [('lot_id', 'ilike', search)]])
                domain += search_domain

            stock_count = StockQuant.search_count(domain)

            pager = portal_pager(
                url="/my/quants",
                total=stock_count,
                page=page,
                step=self._items_per_page
            )

            stock_quants = StockQuant.search(domain,offset=pager['offset'])

            values.update({
                'title': _('Quants'),
                'quant_count': stock_count,
                'stock_quants': stock_quants,
                'page_name': 'quant',
                'pager': pager,
                'default_url': '/my/quants',
                'searchbar_inputs': searchbar_inputs,
            })

            return request.render("konien_portal_stock_quants.portal_my_stock_quants", values)
        except Exception as e:
            return _(str(e))
