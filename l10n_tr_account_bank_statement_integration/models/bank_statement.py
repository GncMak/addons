# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.
import datetime

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
import logging
import io, uuid, json, requests
from suds.client import Client
from suds.plugin import MessagePlugin
from itertools import groupby
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

# test_url = 'http://test.buluttahsilat.com/WebService/WSBankPaymentService.asmx?WSDL'
# test_firmCode = 'C44B613FD1DD474396EF026F94FF8BDE'
# test_username = 'ENTEGRASYONF1580'
# test_password = 'RFQ296*_HZ3-Z77'


def key_func(k):
    return k['FirmBankCode']


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    # payment_id = fields.Char(string='Payment Id')
    bulut_payment_line_id = fields.Many2one(comodel_name='bulut.tahsilat.bank.payment.line', string='Bulut Payment Line')


class BankStatement(models.Model):
    _inherit = 'account.bank.statement'

    blocked_balance = fields.Monetary('Ending Balance', states={'confirm': [('readonly', True)]})
    bulut_bank_code = fields.Char(string='Bulut Bank Code')

    def bank_balance(self, client, bank_iban):
        bulut_service = self.env['bulut.tahsilat.service'].search([])
        return bulut_service.bank_daily_balance_list(datetime.date.today())['BankList']

    # def bank_bulut_payment_line_add(self):
    #     bank_statements = self.env['account.bank.statement'].search([], order="date desc", limit=1)
    #
    #     payment_lists = bank_statements.company_id.bulut_tahsilat_id.bank_payment_list_all(534,
    #                                                                                        datetime.datetime.strptime(
    #                                                                                            bank_statements.date,
    #                                                                                            '%Y-%m-%d').strftime(
    #                                                                                            '%Y-%m-%dT%H:%M:%S'),
    #                                                                                        datetime.datetime.now().strftime(
    #                                                                                            '%Y-%m-%dT%H:%M:%S'))
    #     # raise UserError(payment_lists)
    #
    #     for transaction in payment_lists:
    #         journal = self.env['account.journal'].search([('bulut_bank_code', '=', transaction.FirmBankCode)])
    #         currency_id = self.env['res.currency'].search([('name', '=', transaction.AccountCurrencyCode)])
    #         if transaction.SenderFirmID:
    #             partner = self.env['res.partner'].search([('bulut_sub_firm_id', '=', transaction.SenderFirmID)])
    #
    #         payment_line = self.env['bulut.tahsilat.bank.payment.line']
    #         payment_line.create({
    #             'journal_id': journal.id,
    #             'date': datetime.date.strftime(transaction.PaymentDate, '%Y-%m-%d'),
    #             'amount': transaction.Amount,
    #             'currency_id': currency_id.id,
    #             'partner_id': partner.id,
    #             'note': '',
    #             'state': 'draft',
    #             'firm_bank_code': transaction.FirmBankCode,
    #             'payment_id': transaction.PaymentID,
    #             'payment_type_id': transaction.PaymentTypeID,
    #             'payment_type_explantion': transaction.PaymentTypeExplantion,
    #             'payment_status_type_id': transaction.PaymentStatusTypeID,
    #             'payment_status_type_explantion': transaction.PaymentStatusTypeExplantion,
    #             'sender_firm_id': transaction.SenderFirmID,
    #             'reference_number': transaction.ReferenceNumber,
    #             'voucher_number': transaction.VoucherNumber,
    #             'branch_firm_id': transaction.BranchFirmID,
    #             'branch_firm_name': transaction.BranchFirmName,
    #             'branch_firm_tax_number': transaction.BranchFirmTaxNumber,
    #             'account_type_id': transaction.AccountTypeID,
    #             'function_code1': transaction.FunctionCode1,
    #             'function_code2': transaction.FunctionCode2,
    #             'balance_after_transaction': transaction.BalanceAfterTransaction,
    #         })




        # transaction_sorted = sorted(payment_lists, key=key_func)
        #
        # # bank_balance = bank_statements.company_id.bulut_tahsilat_id.bank_daily_balance_list(
        # #     datetime.datkey_func = {function} <function key_func at 0x7f056c1c7158>e.strftime(payment_lists[0].PaymentDate, '%Y-%m-%d'))
        #
        # for key, transactions in groupby(transaction_sorted, key=key_func):
        #     journal = self.env['account.journal'].search([('bulut_bank_code', '=', key)])
        #     lines = []
        #     total = 0
        #     # end_amount = bank_balance.filtered  # if not bank_balance ... else ...
        #     bank_statement = self.create({
        #         # 'name': datetime.datetime.now(),
        #         'journal_id': journal.id,
        #         'balance_end_real': 0,
        #         'balance_start': 0,
        #     })
        #     for transaction in list(transactions):
        #         line = {
        #             'date': datetime.date.strftime(transaction.PaymentDate, '%Y-%m-%d'),
        #             'name': str(transaction.Explanation),
        #             'amount': transaction.Amount,
        #             'statement_id': bank_statement.id,
        #             'payment_id': transaction.PaymentID,
        #             'payment_type_id': transaction.PaymentTypeID,
        #             'payment_type_explantion': transaction.PaymentTypeExplantion,
        #             'payment_status_type_id': transaction.PaymentStatusTypeID,
        #             'payment_status_type_explantion': transaction.PaymentStatusTypeExplantion,
        #         }
        #         if transaction.SenderFirmID:
        #             partner = self.env['res.partner'].search([('bulut_sub_firm_id', '=', transaction.SenderFirmID)])
        #             line.update({
        #                 'partner_id': partner.id
        #             })
        #         # total += transaction.Amount
        #         lines.append((0, 0, line))
        #
        #     old_bank_statement = self.env['account.bank.statement'].search([('date', '=', datetime.date.strftime(transaction.PaymentDate, '%Y-%m-%d')), ('journal_id', '=', journal.id)])
        #     if old_bank_statement:
        #         bank_statement.update({
        #             'line_ids': lines,
        #         })
        #     else:
        #         bank_statement.write({
        #             'line_ids': lines,
        #             'name': '{date}-{bank_code}-{last_id}'.format(date=datetime.date.strftime(transaction.PaymentDate, '%Y-%m-%d'), bank_code=key, last_id=bank_statements.id+1),
        #             'date': datetime.date.strftime(transaction.PaymentDate, '%Y-%m-%d'),
        #             'date_done': datetime.datetime.now(),
        #             # 'balance_start':
        #             # 'balance_end_real': float(end_amount)
        #             # 'currency_id':
        #         })

    # def bank_statement_create(self):
    #     last_bank_statements = self.env['account.bank.statement'].search([], order='date desc', limit=1)
    #     company_id = self.env.company.id
    #     if not last_bank_statements:
    #         date = relativedelta(days=7)
    #         bulut_service = self.env['res.company']
    #     else:
    #         date = (datetime.datetime.strptime(last_bank_statements[0].date, '%Y-%m-%d') + datetime.timedelta(days=1)).date()
    #     balances = last_bank_statement.company_id.bulut_tahsilat_id.bank_daily_balance(date=date)
    #     if not balances:
    #         return
    #     for balance in balances:
    #         journal = self.env['account.journal'].search([('bulut_bank_code', '=', balance.FirmBankCode)])
    #         self.create({
    #             'date': datetime.date.strftime(balance.LastTimeStamp, '%Y-%m-%d'),
    #             'balance_end_real': balance.Balance,
    #             'blocked_balance': balance.BlockedBalance,
    #             'bulut_bank_code': balance.FirmBankCode,
    #             'journal_id': journal.id
    #             })
        #
        # payment_list = self.env['bulut.tahsilat.bank.payment.line'].search([('state', '=', 'draft')])
        # for payment in payment_list:
        #     journal = self.env['account.journal'].search([('bulut_bank_code', '=', payment.FirmBankCode)])
        #     bank_statement = self.env['account.bank.statement.'].search([('journal_id', '=', journal.id), (
        #     'date', '=', datetime.date.strftime(payment.PaymentDate, '%Y-%m-%d'))])







