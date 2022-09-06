# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.

import io, uuid, json, requests, logging, werkzeug
from odoo import fields, models, _, api, http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from werkzeug import urls

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def bulut_tahsilat_payment(self):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if not self.reconciled and self.state == 'open':
            data = {
                'OrderRefNo': self.name,
                'TotalPrice': self.residual,
                'TotalPriceWithVAT': self.residual,
                'OrderDate': self.date_invoice,
                'Currency': self.currency_id.name,
                'Language': self.partner_id.lang.split('_')[1] if self.partner_id.lang else 'TR',
                # 'BillName': ' '.join([name for name in full_name][0:len(full_name) - 1]),
                # 'BillSurname': full_name[len(full_name) - 1],
                'BillName': self.partner_id.name,
                'BillEmail': self.partner_id.email,
                'BillCompany': self.partner_id.name,
                'BillAddress': self.partner_id.street,
                'BillCity': self.partner_id.state_id.name if self.partner_id.state_id else self.partner_id.city or '',
                'BillCountry': self.partner_id.country_id.name if self.partner_id.country_id else '',
                'DeliveryCity': self.partner_id.state_id.name if self.partner_id.state_id else self.partner_id.city or '',
                'DeliveryCountry': self.partner_id.country_id.name if self.partner_id.country_id else '',
                'ReturnUrl': '{url}/bulut_tahsilat/confirm'.format(url=base_url),
                'PaymentExpCode': self.partner_id.bulut_sub_payment_exp_code or '',
            }
            for line in self.invoice_line_ids.filtered(lambda x: x.product_id != False):
                product = {
                    'ProductName': line.name,
                    'SalePrice': line.price_unit,
                    'SalePriceWithVat': line.price_subtotal,
                    'Quantity': line.quantity,
                    'SaleTotalPrice': line.price_total,
                    'SaleTotalPriceWithVat': line.price_total,
                }
                data.update({'OrderDetailList': [product]})
            req = self.company_id.bulut_tahsilat_id.payment_create_common_page(data)
            if req.StatusCode == 0:
                self.message_post(body=req.PaymentRedirectUrl)
            else:
                self.message_post(body=req.StatusMessage)

            """'{"OrderRefNo":"","StatusCode":"602","StatusMessage":"ISLEM_SIRASINDA_HATA_OLUSTU"}'"""
