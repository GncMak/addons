# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
import logging
import io, uuid, json, requests

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    bulut_payment_id = fields.Char(string='Bulut Payment Id')

    def bank_payment_line_create(self):
        bank_payment_lines = self.env['bulut.tahsilat.bank.payment.line'].search([('state', '=', 'draft'), ('partner_id', '!=', False)])
        for bank_payment_line in bank_payment_lines:
            if self.search([('bulut_payment_id', '=', bank_payment_line.PaymentID)]):
                continue
            if bank_payment_line.partner_id:
                payment_type = 'inbound' if bank_payment_line.amount > 0 else 'outbound'
            else:
                payment_type = 'transfer'
            account_payment = {
                'journal_id': bank_payment_line.journal_id.id,
                'amount': bank_payment_line.amount,
                'currency_id': bank_payment_line.currency_id.id,
                'payment_date': bank_payment_line.date,
                'company_id': bank_payment_line.company_id.id,
                'state': 'posted',
                'payment_type': payment_type,
            }
            if payment_type == 'transfer':
                account_payment.update({
                    'destination_journal_id': 1
                })

            pass


