# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
import io, uuid, json, requests, datetime, logging

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    # bulut_bank_code = fields.Char(string='Bulut Bank Code')
    blocked_balance = fields.Char(string='BlockedBalance')

    # def bank_payment_add(self):
    #     bulut_service = self.env['bulut.tahsilat.service'].search([])
    #     payment_lists = bulut_service.bank_payment_list_all(531, '2022-07-01T01:00:00', '2022-08-01T23:59:59')
    #     raise UserError(payment_lists)
        # for i in payment_lists:
        #     amount = i.Amount
        #     self.write({
        #         'ref': datetime.datetime.now(),
        #     })
