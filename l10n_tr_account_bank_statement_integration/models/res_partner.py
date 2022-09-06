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

    def action_bulut_tahsilat_sub_firm(self):
        partners = self.search([('bulut_sub_firm_id', '=', False), ('company_type', '=', 'company')])
        for partner in partners:
            if partner.bulut_sub_firm_id:
                partner.company_id.bulut_tahsilat_id.sub_firm_update(partner)
            else:
                partner.company_id.bulut_tahsilat_id.sub_firm_add(partner)

    def balance_payment_send(self):
        """
        Müşterilerin Toplam borcu için ödeme lnki gönderme.
        """
        for partner in self:
            request = ("SELECT * from ...")
            self.env.cr.execute(request)
            balance = self.env.cr.dictfetchall()
            raise UserError(balance)
