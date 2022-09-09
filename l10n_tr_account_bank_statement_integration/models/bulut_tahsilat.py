# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
import datetime, io, uuid, json, requests, logging, phonenumbers
from suds import *
from suds.client import Client
from suds.plugin import MessagePlugin
from odoo import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class BankPaymentList(models.Model):
    _name = 'bulut.tahsilat.bank.payment.line'
    _description = ''

    company_id = fields.Many2one(comodel_name='res.company', string='Company', help='', copy=False)
    journal_id = fields.Many2one(comodel_name='account.journal', string='Journal')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', copy=False)
    product_id = fields.Many2one(comodel_name='product.product', string='Product', copy=False)
    currency_id = fields.Many2one(comodel_name='res.currency', help='', readonly=True)
    payment_id = fields.Many2one(comodel_name='account.payment', string='Payment', copy=False, help='')
    expense_id = fields.Many2one(comodel_name='hr.expense', string='Expense')
    account_id = fields.Many2one(comodel_name='account.account', string='Account', copy=False, help='')
    move_id = fields.Many2one(comodel_name='account.move', string='Account Move', copy='False', help='')
    name = fields.Char(string='Name', copy=False, help='')
    amount = fields.Monetary(digits=4, copy=False)
    date = fields.Date(required=True, copy=False, default=fields.Date.context_today, readonly=True)
    statement_line_id = fields.Many2one(comodel_name='account.bank.statement.line', string='Statement Line', copy=False)
    note = fields.Text(string='Notes', copy=False)
    state = fields.Selection(selection=[('draft', 'Draft'), ('cancel', 'Cancelled'), ('done', 'Done')], string='Status', readonly=True)
    firm_bank_code = fields.Char(string='Bank Code')
    firm_bank_iban = fields.Char(string='Bank IBAN')
    bulut_payment_id = fields.Char(string='Bulut Payment Id', copy=False)
    explanation = fields.Text(string='Explanation', copy=False)
    payment_type_id = fields.Integer(string='Payment Type Id')
    payment_type_explantion = fields.Char(string='Payment Type Explantion')
    payment_status_type_id = fields.Integer(string='Payment Status Type ID')
    payment_status_type_explantion = fields.Char(string='Payment Status Type Explantion')
    sender_firm_name = fields.Char(string='Sender Firm Name', copy=False)
    sender_firm_id = fields.Char(string='Sender Firm Id', copy=False)
    sender_firm_code = fields.Char(string='Sender Firm Code', copy=False)
    sender_firm_bank_iban = fields.Char(string='Sender Firm Bank IBAN', copy=False)
    reference_number = fields.Char(string='Reference Number', copy=False)
    voucher_number = fields.Char(string='VoucherNumber', copy=False)
    branch_firm_id = fields.Char(string='BranchFirmID', copy=False)
    payment_exp_code = fields.Char(string='PaymentExpCode', copy=False)
    tax_number = fields.Char(string='TaxNumber', copy=False)
    branch_firm_name = fields.Char(string='BranchFirmName', copy=False)
    branch_firm_tax_number = fields.Char(string='BranchFirmTaxNumber', copy=False)
    account_type_id = fields.Char(string='AccountTypeID', copy=False)
    function_code1 = fields.Char(string='FunctionCode1', copy=False)
    function_code2 = fields.Char(string='FunctionCode2', copy=False)
    balance_after_transaction = fields.Monetary(string='BalanceAfterTransaction', copy=False)

    """
    Ödeme tipi
        512: KREDİ
        516: ÇEK
        513: BANKA HAREKETİ
        517: POS
        514: NAKİT
        518: MASRAF
        515: VİRMAN
        519: SENET
    """

    def payment_line_add(self):
        bulut_services = self.env['bulut.tahsilat.service'].search([('state', '=', 'Active')])
        for bulut_service in bulut_services:
            last_bulut_payment_line = self.search([], order='date desc', limit=1)
            start_date = datetime.datetime.strptime(last_bulut_payment_line.date, '%Y-%m-%d').strftime(
                '%Y-%m-%dT%H:%M:%S') if last_bulut_payment_line else (
                        datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%S')
            end_date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            payment_list_534 = bulut_service.bank_payment_list_all(534, '2022-06-01T00:00:00', end_date)
            # EŞLEŞME ler manuel yapılmalı.
            payment_list_531 = bulut_service.bank_payment_list_all(531, '2022-06-01T00:00:00', end_date)

            payment_list = []
            if payment_list_534:
                payment_list = payment_list + payment_list_534
            if payment_list_531:
                payment_list = payment_list + payment_list_531
            # INFO: Eşleşmemiş(534) kayıtlar da olabileceği için hem eşleşen hem eşleşmeyenleri alıyoruz.
            # Bu "eşleşme" Bulut Tahsilat tarafındaki bir statü. Odoo statuleri değil.

            if not payment_list:
                continue
            for transaction in payment_list:
                transaction = Client.dict(transaction)
                if self.search([('bulut_payment_id', '=', transaction.get('PaymentID', False))]):
                    continue
                journal = self.env['account.journal'].search(
                    [('bank_account_id.acc_number', '=', str(transaction.get('FirmBankIBAN', False)).replace(' ', ''))])
                if not journal or len(journal) > 1:
                    continue
                currency_id = self.env['res.currency'].search(
                    [('name', '=', transaction.get('AccountCurrencyCode', False))])

                # if transaction.get('SenderFirmID', False):
                partner = self.env['res.partner'].search(
                    [('bulut_sub_firm_id', '=', str(transaction.get('SenderFirmID', False)))]) if transaction.get(
                    'SenderFirmID', False) else None
                if not partner:

                    partner = self.env['res.partner'].search(
                        [('bulut_sub_firm_code', '=', transaction.get('SenderFirmCode', False))]) if transaction.get(
                        'SenderFirmCode', False) else None
                if not partner:
                    # if transaction.get('SenderFirmBankIBAN', False):
                    partner = self.env['res.partner.bank'].search(
                        [('acc_number', '=', transaction.get('SenderFirmBankIBAN'))]).partner_id if transaction.get(
                        'SenderFirmBankIBAN') else None

                if transaction.get('PaymentTypeID', False) == 518:  # Masraf
                    product = self.env['product.template'].search(
                        [('bulut_tahsilat_expense_code', '=', transaction.get('FunctionCode1', False))])
                else:
                    product = None

                payment_line = self.create({
                    'journal_id': journal.id,
                    'company_id': journal.company_id.id,
                    'name': '{}-{}'.format(transaction.get('PaymentID', ''), transaction.get('ReferenceNumber', '')),
                    'date': datetime.date.strftime(transaction.get('PaymentDate', datetime.datetime.now()), '%Y-%m-%d'),
                    'amount': transaction.get('Amount', 0),
                    'currency_id': currency_id.id,
                    'partner_id': partner.id if partner else None,
                    'product_id': product.id if product else None,
                    'note': '',
                    'state': 'draft',
                    'firm_bank_code': transaction.get('FirmBankCode', False),
                    'firm_bank_iban': transaction.get('FirmBankIBAN', False),
                    'bulut_payment_id': transaction.get('PaymentID', False),
                    'explanation': transaction.get('Explanation', False),
                    'payment_type_id': transaction.get('PaymentTypeID', False),
                    'payment_type_explantion': transaction.get('PaymentTypeExplantion', False),
                    'payment_status_type_id': transaction.get('PaymentStatusTypeID', False),
                    'payment_status_type_explantion': transaction.get('PaymentStatusTypeExplantion', False),
                    'sender_firm_name': transaction.get('SenderFirmName', False),
                    'sender_firm_id': transaction.get('SenderFirmID', False),
                    'sender_firm_code': transaction.get('SenderFirmCode', False),
                    'sender_firm_bank_iban': transaction.get('SenderFirmBankIBAN', False),
                    'reference_number': transaction.get('ReferenceNumber', False),
                    'voucher_number': transaction.get('VoucherNumber', False),
                    'payment_exp_code': transaction.get('PaymentExpCode', False),
                    'tax_number': transaction.get('TaxNumber', False),
                    'branch_firm_id': transaction.get('BranchFirmID', False),
                    'branch_firm_name': transaction.get('BranchFirmName', False),
                    'branch_firm_tax_number': transaction.get('BranchFirmTaxNumber', False),
                    'account_type_id': transaction.get('AccountTypeID', False),
                    'function_code1': transaction.get('FunctionCode1', False),
                    'function_code2': transaction.get('FunctionCode2', False),
                    'balance_after_transaction': transaction.get('BalanceAfterTransaction', False),
                })
                self._cr.commit()
                # if payment_line.payment_status_type_id == 531:
                #     payment_line.company_id.bulut_tahsilat_id.update_payment_status_info(payment_line)
                # if payment_line.payment_status_type_id == 534 and payment_line.payment_exp_code:
                #     payment_line.company_id.bulut_tahsilat_id.update_payment_status_info_with_exp_code(payment_line)

    def payment_line_process(self):
        for line in self.search([('state', '=', 'draft')]):
            # TODO: Eğer Partner ve destination_journal boş olursa o zaman kredi/senet/Çek vs ödemesi gibi bir şeydir.
            # TODO: Bu durumda, yevmiye fişi oluşturmak mantıklı. (Sormak lazım)
            if not line.journal_id:
                continue
            if line.payment_type_id != 518:
                partner_type = False
                if line.partner_id:
                    partner_type = 'supplier' if line.amount < 0 else 'customer'

                destination_journal = self.env['account.journal'].search(
                    [('bank_account_id.acc_number', '=', line.sender_firm_bank_iban),
                     ('company_id', '=', line.company_id.id)])
                if destination_journal:
                    payment_type = 'transfer'
                else:
                    payment_type = line.amount > 0 and 'inbound' or 'outbound'

                payment_methods = (line.amount > 0) and line.journal_id.inbound_payment_method_ids or line.journal_id.outbound_payment_method_ids

                pre_payment = {
                    'payment_method_id': payment_methods and payment_methods[0].id or False,  # TODO:
                    'payment_type': payment_type,
                    'partner_type': partner_type,
                    'journal_id': line.journal_id.id,
                    'payment_date': line.date,
                    'state': 'draft',
                    'currency_id': line.currency_id.id,
                    'amount': abs(line.amount),
                    'communication': line.explanation,
                    'name': line.name
                }

                if destination_journal:
                    pre_payment.update({
                        'destination_journal_id': destination_journal.id
                    })
                if line.partner_id:
                    pre_payment.update({
                        'partner_id': line.partner_id.id,
                    })

                payment = self.env['account.payment'].create(pre_payment)
                payment.post()
                line.write({
                    'payment_id': payment.id,
                    'state': 'done'
                })

    def expense_create(self):
        # TODO: Check
        self.ensure_one()
        expense = self.env['hr.expense'].create({
            'name': self.explanation,
            'date': self.date,
            # 'employee_id': SUPERUSER_ID,
            'product_id': self.product_id.id,
            'unit_amount': abs(self.amount),
            'quantity': 1,
            'payment_mode': 'company_account',
            'reference': self.reference_number,
            # 'sheet_id': self.expense_sheet.id,
            })
        self.write({
            'expense_id': expense.id,
            'state': 'done'
        })
        expense.submit_expenses()
        # expense.approve_expense_sheets()
        # expense.action_sheet_move_create()

    def account_move_create(self):
        # TODO:
        move_id = self.env['account.move'].create({

        })
        self.write({
            'move_id': move_id.id,
            'state': 'done'
        })



class BulutTahsilatSettings(models.Model):
    _name = 'bulut.tahsilat.service'
    _description = 'Bulut Tahsilat Integration Service'

    name = fields.Char(string='Service Name')
    service_url = fields.Char(string='Service Url', help='', copy=False)
    username = fields.Char(string='Service Username', help='', copy=False)
    password = fields.Char(string='Service Password', help='', copy=False)
    firm_code = fields.Char(string='Service FirmCode', help='', copy=False)
    secret_key_code = fields.Char(string='Service Secret Keyt Code', help='', copy=False)
    state = fields.Selection(
        selection=[
            ('Active', 'Active'),
            ('Passive', 'Passive')],
        string='State', help='', copy=False)

    @staticmethod
    def phone_number_replace(param, country):
        phone = None
        if len(param) > 15:  # INFO: Telefon numarası yerine boşluk veya farklı dataların olmasından dolayı.
            return phone
        try:
            phone_number = phonenumbers.parse(param, region=country.code)
            phone = str(phone_number.national_number)
            if len(phone) < 11:
                difference = ''.join(['0' for i in range(10 - len(phone))])
                phone = '{}{}'.format(difference, phone)
            return phone
        except Exception as e:
            _logger.error(_("Bulut Tahsilat,  Partner Phone Number Error") + '\n\n' + e)
        finally:
            return phone

        # return '0{phone}'.format(phone=phone_number.national_number)

    def key_func(k):
        return k['FirmBankCode']

    def get_client(self):
        service = self.env['bulut.tahsilat.service'].search([('state', '=', 'Active')])
        return Client(service.service_url)

    def sub_firm_update(self, partner):
        pass

    def sub_firm_add(self, partners):
        service = Client(self.service_url)
        for partner in partners:
            sub_firm_model = service.factory.create('SubFirm')
            enum_status = service.factory.create('EnumStatus')
            enum_status.__setitem__ = 'Active'

            contact_name = ''
            partner_child = None
            try:
                partner_child = partner.mapped('child_ids').filtered(lambda x: x.type == 'contact')[0] if partner.child_ids else None
            except:
                pass
            finally:
                partner_child = None

            if partner_child:
                contact_name = partner_child.name

            country = partner.country_id or self.env.user.company_id.country_id

            try:  # INFO:  İl/Eyalet Kodu 06 olması gerekirken Ankara veya 06378 gibi anlamsız datalar var.
                city_id = str(int(partner.state_id.code)) if (partner.state_id and partner.country_id.id == partner.company_id.country_id.id) else '1'
            except:
                pass
            finally:
                city_id = '1'

            sub_firm_model.FirmName = partner.name
            sub_firm_model.Address = ('{address}'.format(
                address=partner.street if not partner.street2 else partner.street + ' ' + partner.street2)) if partner.street else None
            sub_firm_model.County = partner.city or ''
            sub_firm_model.CityID = city_id
            sub_firm_model.Phone = self.phone_number_replace(partner.phone, country) if partner.phone else None
            sub_firm_model.TaxOffice = partner.tax_office_id.name if partner.tax_office_id else ' '
            sub_firm_model.TaxNumber = (partner.vat[2:] if partner.vat.startswith('TR') else partner.vat) if partner.vat else ''
            sub_firm_model.AuthPersName = ' '.join([name for name in contact_name.split()][0:len(contact_name.split()) - 1])
            sub_firm_model.AuthPersSurname = contact_name.split()[len(contact_name.split()) - 1] if contact_name else None
            sub_firm_model.AuthPersGSM = (self.phone_number_replace(partner_child.phone, country) if partner_child.phone else None) if partner_child else None,
            sub_firm_model.AuthPersGenderID = '0'
            sub_firm_model.Status = enum_status.__setitem__
            # sub_firm_model.Status = 'Active'
            sub_firm_model.DealerCode = str(partner.id)
            sub_firm_model.BusinessArea = partner.industry_id.name if partner.industry_id else ''
            sub_firm_model.AccountingCode = '120' if partner.customer else '320'
            sub_firm_model.ReservedField = ''

            sub_firm_response = service.service.SubFirmAddNew(self.username, self.password, self.firm_code, sub_firm_model)
            if sub_firm_response.StatusCode == 0:
                partner.write({
                    'bulut_sub_firm_id': sub_firm_response['SubFirmReturn']['FirmID'],
                    'bulut_sub_firm_code': sub_firm_response['SubFirmReturn']['FirmCode'],
                    'bulut_sub_payment_exp_code': sub_firm_response['SubFirmReturn']['PaymentExpCode'],
                })
                self._cr.commit()
            else:
                partner.message_post(body='Bulut Tahsilat : %s' % sub_firm_response.StatusMessage)
                # raise UserError(sub_firm_response.StatusMessage)

    def sub_firm_list(self):
        service = Client(self.service_url)

        firm_list = service.service.SubFirmList(self.username, self.password, self.firm_code)
        for i in firm_list:
            return

    def sub_firm_iban_add(self, data):
        for item in data:
            client = Client(self.service_url)
            sub_firm_iban_add = client.service.SubFirmIBANAddNew(self.username, self.password, self.firm_code,
                                                                 item.get('paymentExpCode', False),
                                                                 item.get('iban', False), item.get('bankCode', False))
            if sub_firm_iban_add.StatusCode == 0:
                item.get('partner').message_post(body=sub_firm_iban_add.StatusMessage)
                item.get('bank_account').write({
                    'bulut_sync': True
                })
            else:
                item.get('partner').message_post(body='{}\n\n{}'.format(sub_firm_iban_add.StatusMessage, item))
            self._cr.commit()

    def sub_firm_iban_delete(self, data):
        for item in data:
            client = Client(self.service_url)
            sub_firm_iban_add = client.service.SubFirmIBANDelete(self.username, self.password, self.firm_code, item.get('paymentExpCode', False), item.get('iban', False), item.get('bankCode', False))
            if sub_firm_iban_add.StatusCode == 0:
                item.get('partner').message_post(body='Bulut Tahsilat Partner IBAN Add Message: {}'.format(sub_firm_iban_add.StatusMessage))
                item.get('bank_account').write({
                    'bulut_sync': True
                })
            else:
                item.get('partner').message_post(body='Bulut Tahsilat Partner IBAN Add Error Message: {}\n\n{}'.format(sub_firm_iban_add.StatusMessage, item))
            self._cr.commit()

    def sub_firm_vkn_add(self, data):
        for item in data:
            client = Client(self.service_url)
            response = client.service.SubFirmVKNAddNew(self.username, self.password, self.firm_code,
                                                       item.get('paymentExpCode', False), item.get('vat', False))
            if response.StatusCode == 0:
                item.get('partner').message_post(body=response.StatusMessage)
                item.get('partner').write({
                    'bulut_sub_firm_vkn_id': response.SubFirmVKNID
                })
            else:
                item.get('partner').message_post(body='{}\n\n{}'.format(response.StatusMessage, item))
            self._cr.commit()

    def bank_payment_list_all(self, payment_status_type, start_date, end_date):
        service = Client(self.service_url)
        payment_lists = service.service.BankPaymentListAll(self.username, self.password, self.firm_code,
                                                           payment_status_type, start_date, end_date)
        return payment_lists['BankPaymentListItem'] if payment_lists else None

    def bank_daily_balance(self, date):
        service = Client(self.service_url)
        try:
            response = service.service.GetFirmBankDailyBalance(userName=self.username, password=self.password,
                                                               firmAPICode=self.firm_code, iban='', date=date)
            if response and response.StatusCode == 0:
                return Client.dict(response['BankList']).get('BankBalance')
            return None
        except:
            return None

    def payment_create_common_page(self, data):
        # service = Client(self.service_url)
        data.update({
            'UserName': self.username,
            'Password': self.password,
            'FirmAPICode': self.firm_code,
            'Hash': hash(
                '{SecretKeyCode}{UserName}{FirmAPICode}{OrderRefNo}{OrderDate}{TotalPriceWithVat}{Currency}'.format(
                    SecretKeyCode=self.secret_key_code, UserName=self.username, FirmAPICode=self.firm_code,
                    OrderRefNo=data['OrderRefNo'], OrderDate=data['OrderDate'],
                    TotalPriceWithVat=data['TotalPriceWithVAT'], Currency=data['Currency'])),
        })

        return requests.get('https://portal.buluttahsilat.com/Api/Vpos/PaymentCreateCommonPage', 'post', data=data)

    def update_payment_status_info(self, bank_payment_line):
        service = Client(self.service_url)
        try:
            response = service.service.UpdatePaymentStatusInfo(self.username, self.password,
                                                               self.firm_code, bank_payment_line.bulut_payment_id,
                                                               532)
            if response == 'OK':
                bank_payment_line.update({
                    'payment_status_type_id': 532,
                    'payment_status_type_explantion': 'TAMAMLANDI'
                })
            else:
                bank_payment_line.update({'note': response})
            self._cr.commit()
        except Exception as e:
            bank_payment_line.update({'note': e})

    def update_payment_status_info_with_exp_code(self, bank_payment_line):
        service = Client(self.service_url)
        try:
            response = service.service.UpdatePaymentStatusInfoWithPaymentExpCode(self.username, self.password,
                                                                                 self.firm_code,
                                                                                 bank_payment_line.bulut_payment_id,
                                                                                 bank_payment_line.payment_exp_code,
                                                                                 532)
            if response and response.StatusCode == 0:
                bank_payment_line.update({
                    'payment_status_type_id': 532,
                    'payment_status_type_explantion': 'TAMAMLANDI'
                })
            else:
                bank_payment_line.update({'note': response.StatusMessage})
            self._cr.commit()
        except Exception as e:
            bank_payment_line.update({'note': e})


# class BulutTahsilatService:
#     def __init__(self, prod=False, params=None):
#         self.url = params.get('url')
#         self.userName = params.get('userName')
#         self.userName = params.get('password')
#         self.userName = params.get('firmCode')
#
#
# class SubFirm:
#     def __init__(self, params=None):
#         self.userName = params.get('userName')
#         self.password = params.get('password')
#         self.firmCode = params.get('firmCode')
#         self.FirmName = params.FirmName
#         self.Address = params.Address
#         self.County = params.County
#         self.CityID = params.CityID
#         self.Phone = params.Phone
#         self.TaxOffice = params.TaxOffice
#         self.TaxNumber = params.TaxNumber
#         self.AuthPersName = params.AuthPersName
#         self.AuthPersSurname = params.AuthPersSurname
#         self.AuthPersGSM = params.AuthPersGSM
#         self.AuthPersGenderID = params.AuthPersGenderID
#         self.Status = params.Status
#         self.DealerCode = params.DealerCode
#         self.BusinessArea = params.BusinessArea
#         self.AccountingCode = params.AccountingCode
#         self.ReservedField = params.ReservedField
#
#
# class SubFirmList:
#     def __init__(self, params=None):
#         self.userName = params.get('userName')
#         self.password = params.get('password')
#         self.firmCode = params.get('firmCode')
