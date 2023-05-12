from odoo import api, fields, models,_


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_config_start(self):
        """Return action to start configuration wizard"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.configurator.purchase',
            'name': "Product Configurator",
            'view_mode': 'form',
            'target': 'new',
            'context': dict(
                self.env.context,
                default_order_id=self.id,
                wizard_model='product.configurator.purchase',
            ),
        }


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    custom_value_ids = fields.One2many(
        comodel_name='product.attribute.value.custom',
        inverse_name='product_id',
        related="product_id.value_custom_ids",
        string="Custom Values"
    )
    config_ok = fields.Boolean(
        related="product_id.config_ok",
        string="Configurable",
        readonly=True
    )

    @api.multi
    def reconfigure_product(self):
        """ Creates and launches a product configurator wizard with a linked
        template and variant in order to re-configure a existing product. It is
        esetially a shortcut to pre-fill configuration data of a variant"""
        wizard_model = 'product.configurator.purchase'
        extra_vals = {
            'order_id': self.order_id.id,
            'order_line_id': self.id,
            'product_id': self.product_id.id,
        }
        self = self.with_context({
            'default_order_id': self.order_id.id,
            'default_order_line_id': self.id
        })

        return self.product_id.product_tmpl_id.create_config_wizard(
            model_name=wizard_model, extra_vals=extra_vals
        )

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        # Reset date, price and quantity since _onchange_quantity will provide default values
        #self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context(
            lang=self.partner_id.lang,
            partner_id=self.partner_id.id,
        )

        if self.config_ok:
            product = self.product_id.with_context(
                lang=self.partner_id.lang).browse(self.product_id.id)
            convert_name = product.name + "\n"
            for attrib_line in product.attribute_value_ids:
                convert_name += _(attrib_line.display_name) + "\n"
            self.name = convert_name
        else:
            self.name = product_lang.display_name
            if product_lang.description_purchase:
                self.name += '\n' + product_lang.description_purchase

        fpos = self.order_id.fiscal_position_id
        #if self.env.uid == SUPERUSER_ID:
        #    company_id = self.env.user.company_id.id
        #    self.taxes_id = fpos.map_tax(
        #        self.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
        #else:
        self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id)

        self._suggest_quantity()
        self._onchange_quantity()

        return result
