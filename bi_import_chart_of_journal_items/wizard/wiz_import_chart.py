# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime
import tempfile
import binascii
import xlrd
from datetime import date, datetime
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, _
import logging

_logger = logging.getLogger(__name__)
import io

try:
	import csv
except ImportError:
	_logger.debug('Cannot `import csv`.')
try:
	import xlwt
except ImportError:
	_logger.debug('Cannot `import xlwt`.')
try:
	import cStringIO
except ImportError:
	_logger.debug('Cannot `import cStringIO`.')
try:
	import base64
except ImportError:
	_logger.debug('Cannot `import base64`.')


class ImportChartJournalItems(models.TransientModel):
	_name = "import.chart.journal.items"

	File_select = fields.Binary(string="Select Excel File")
	import_option = fields.Selection([('xls', 'XLS File')], string='Select', default='xls')
	date = fields.Date(string="Tarih", required=True)
	company_id = fields.Many2one('res.company', string="Company", required=True)
	journal_id = fields.Many2one('account.journal', string="Journal", required=True)

	@api.multi
	def import_file(self):
		movelines = []
		analytic_account_id = None
		if self.import_option in ['xls', 'xlsx']:
			try:
				fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
				fp.write(binascii.a2b_base64(self.File_select))
				fp.seek(0)
				values = {}
				workbook = xlrd.open_workbook(fp.name)
				sheet = workbook.sheet_by_index(0)

			except:
				raise Warning(_("Invalid file!"))

			for row_no in range(sheet.nrows):
				val = {}
				if row_no <= 0:
					fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
				else:

					line = list(
						map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value),
							sheet.row(row_no)))

					values.update({
						'account_code': str(line[0]),
						'partner': str(line[1]),
						'description': str(line[2]),
						'analytic_account': str(line[3]),
						'debit': float(line[4]),
						'credit': float(line[5]),
					})

					account_id = self.env['account.account'].search([('code', '=', str(values.get('account_code'))), ('company_id', '=', self.company_id.id)])
					if not account_id:
						raise Warning(_('Girdiğiniz hesap kodu sistemde bulunamadı. Lütfen hesap kodunu inceleyin ve tekrar yüklemeyi deneyin.'))

					partner_id = None
					if values.get('partner'):
						partner_id = self.env['res.partner'].search([('name', '=', values.get('partner')), ('active', '=', True), ('employee', '=', True)], limit=1)
						if not partner_id:
							raise Warning(_('Bu isimde bir personel bulunamamıştır. Personel ismini düzeltip tekrar deneyiniz.'))

					analytic_account_id = None
					if values.get('analytic_account'):
						analytic_account_id = self.env['account.analytic.account'].search([('name', '=', values.get('analytic_account')), ('active', '=', True)], limit=1)
						if not analytic_account_id:
							raise Warning(_('Bu isimde bir analitik hesap bulunamamıştır. Analitik hesap ismini düzeltip tekrar deneyiniz.'))

					res = self.create_chart_journal_items(values)

					moveline = (0, 0, {
						'date': self.date,
						'date_maturity': self.date,
						'account_id': account_id.id,
						'company_id': self.company_id.id,
						'journal_id': self.journal_id.id,
						'partner_id': partner_id.id if partner_id else None,
						'analytic_account_id': analytic_account_id.id if analytic_account_id else None,
						'name': values.get('description'),
						'debit': float(values.get('debit')),
						'credit': float(values.get('credit')),
					})
					movelines.append(moveline)

		else:
			raise Warning(_("Please select any one from xls formate!"))

		account_move = self.env['account.move'].create({
			'date': self.date,
			'company_id': self.company_id.id,
			'journal_id': self.journal_id.id,
			'ref': self.date + ' Bordrosu',
			'closing_type': 'none',
			'document_type': 'other',
			'document_type_description': 'Ücret Bordrosu İcmali',
			'document_date': self.date,
			'line_ids': movelines,
		})

		return res

	@api.multi
	def create_chart_journal_items(self, values):

		if values.get("account_code") == "" or not values.get("account_code"):
			raise Warning(_('Code field cannot be empty.'))
