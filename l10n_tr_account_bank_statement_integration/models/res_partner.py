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
    bulut_sub_firm_vkn_id = fields.Integer(string='SubFirmVKNID')

    @api.multi
    def bulut_tahsilat_sub_firm(self):
        """
        Bulut Tahsilat'a tüm müşteri/tedarikçi contact'ları ekliyoruz.
        Her bir partneri bağlı olduğu company e göre gönderiyoruz.
        """

        partners = self.search([('is_company', '=', True), ('bulut_sub_firm_id', '=', False), ('vat', '!=', False),
                                ('parent_id', '=', False)])
        # ('company_id.bulut_tahsilat_id', '!=', False)
        bulut_tahsilat = self.env['bulut.tahsilat.service'].search([('state', '=', 'Active')])
        if len(bulut_tahsilat) > 1:
            # MultiCompany, Bulut Tahsilatta her bir company için ayrı hesap tanımlanmış ve cariler ortak olmayacak ise
            # Her bir Company için carileri ayrı ayrı gönderiyoruz. Eğer Ortak kullanılacak ise "else" düşüp
            # tek bir hesap altında gönderiyoruz.
            for partner in partners:
                partner.company_id.bulut_tahsilat_id.sub_firm_add([partner])
        else:
            bulut_tahsilat.sub_firm_add(partners)


    def action_bulut_tahsilat_sub_firm_update(self):
        self.ensure_one()
        self.company_id.bulut_tahsilat_id.sub_firm_update(self)

    def partner_iban_add(self):
        """
        Partner'ların IBANlarını Bulut Tahsilata ekliyoruz.
        """
        services = self.env['bulut.tahsilat.service'].search([('state', '=', 'Active')])

        partners = self.env['res.partner'].search([('bulut_sub_firm_id', '!=', False)])
        data = []
        for bank_account in partners.mapped('bank_ids').filtered(lambda x: not x.bulut_sync):
            if len(bank_account.acc_number) < 20 or len(bank_account.acc_number) > 35:
                continue
            data_line = {
                'company_id': bank_account.partner_id.company_id,
                'bank_account': bank_account,
                'partner': bank_account.partner_id,
                'paymentExpCode': bank_account.partner_id.bulut_sub_payment_exp_code,
                'iban': bank_account.acc_number.replace(' ', ''),
                'bankCode': str(int(bank_account.acc_number.replace(' ', '')[4:9]))  # Banka EFT_CODE'u IBAN'dan buluyoruz
            }
            data.append(data_line)
        res = {}
        [res.setdefault(i['company_id'], []).append(i) for i in data]
        # MultiCompany durumunda her company'nin kendi bulut hesabındaki carilere ayrı ayrı işlem yapması için.
        for company_id, items in res.items():
            if len(services) > 1:
                # MultiCompany de Bulut Tahsilatta her bir company için hesap tanımlanmış ve cariler ortak olmayacak ise
                # Her bir Company için carileri ayrı ayrı gönderiyoruz. Eğer Ortak kullanılacak ise "else" düşüp
                # tek bir hesap altında gönderiyoruz. O yüzden yukarıdaki gruplamayı yaptık.
                if company_id.bulut_tahsilat_id:
                    company_id.bulut_tahsilat_id.sub_firm_iban_add(items)
            else:
                services.sub_firm_iban_add(items)

    def partner_vkn_add(self):
        """
        Partner'ların VKNlarını Bulut Tahsilata ekliyoruz.
        """
        services = self.env['bulut.tahsilat.service'].search([('state', '=', 'Active')])

        partners = self.env['res.partner'].search(
            [('bulut_sub_firm_id', '!=', False), ('bulut_sub_firm_vkn_id', '=', False)])
        data = []
        for partner in partners:
            data_line = {
                'company_id': partner.company_id,
                'partner': partner,
                'paymentExpCode': partner.bulut_sub_payment_exp_code,
                'vat': partner.vat[2:] if partner.vat.startswith('TR') else partner.vat
            }
            data.append(data_line)
        res = {}
        [res.setdefault(i['company_id'], []).append(i) for i in data]
        # MultiCompany durumunda her company'nin kendi bulut hesabındaki carilere ayrı ayrı işlem yapması için.
        for company_id, items in res.items():
            if len(services) > 1:
                # MultiCompany de Bulut Tahsilatta her bir company için hesap tanımlanmış ve cariler ortak olmayacak ise
                # Her bir Company için carileri ayrı ayrı gönderiyoruz. Eğer Ortak kullanılacak ise "else" düşüp
                # tek bir hesap altında gönderiyoruz. O yüzden yukarıdaki gruplamayı yaptık.
                if company_id.bulut_tahsilat_id:
                    company_id.bulut_tahsilat_id.sub_firm_vkn_add(items)
            else:
                services.sub_firm_vkn_add(items)

    def balance_payment_send(self):
        pass
        """
        Müşterilerin Toplam borcu için ödeme linki gönderme.
        """
        # TODO: Bulut tahsilat Sanal POS devreye alınınca tamamlanacak.
        for partner in self:
            request = ("SELECT * from ...")
            self.env.cr.execute(request)
            balance = self.env.cr.dictfetchall()
            raise UserError(balance)
