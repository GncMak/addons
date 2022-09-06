# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
import logging
import io, uuid, json, requests

_logger = logging.getLogger(__name__)


class Partners(models.Model):
    _inherit = 'res.partner'

    bulut_sub_firm_id = fields.Char(string='Bulut Tahsilat Firma Id', help='')
    bulut_sub_firm_code = fields.Char(string='Bulut Tahsilat Firma Kodu', help='')
    bulut_sub_payment_exp_code = fields.Char(string='Bulut Tahsilat Firma Payment Exp Code', help='')

    def bulut_tahsilat_sub_firm(self):
        """"""
        partners = self.search([('is_company', '=', True), ('bulut_sub_firm_id', '=', False),
                                ('company_id.bulut_tahsilat_id', '!=', False)])
        for partner in partners:
            partner.company_id.bulut_tahsilat_id.sub_firm_add(partner)

    def action_bulut_tahsilat_sub_firm_update(self):
        self.ensure_one()
        self.company_id.bulut_tahsilat_id.sub_firm_update(self)

    def partner_iban_add(self):
        partners = self.env['res.partner'].search([('bank_account_count', '>', 0), ('is_company', '=', True)])
        data = []
        s = partners.mapped('bank_ids').filtered(lambda x: not x.bulut_sync)
        for bank_account in partners.mapped('bank_ids').filtered(lambda x: not x.bulut_sync):
            # for bank_account in partner.bank_ids.filtered(lambda x: not x.bulut_sync):
            data_line = {
                'company_id': bank_account.partner_id.company_id,
                'partner': bank_account.partner_id,
                'paymentExpCode': bank_account.partner_id.bulut_sub_payment_exp_code,
                'iban': bank_account.acc_number.replace(' ', ''),
                'bankCode': str(int(bank_account.acc_number.replace(' ', '')[4:9]))
            }
            data.append(data_line)
        res = {}
        [res.setdefault(i['company_id'], []).append(i) for i in data]
        for company_id, items in res.items():
            company_id.bulut_tahsilat_id.partner_iban_add(items)


    def balance_payment_send(self):
        """
        Müşterilerin Toplam borcu için ödeme lnki gönderme.
        """
        for partner in self:
            request = ("SELECT * from ...")
            self.env.cr.execute(request)
            balance = self.env.cr.dictfetchall()
            raise UserError(balance)
