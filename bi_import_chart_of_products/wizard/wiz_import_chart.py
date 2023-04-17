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

class ImportChartProduct(models.TransientModel):
	_name = "import.chart.product"

	File_select = fields.Binary(string="Select Excel File")
	import_option = fields.Selection([('xls', 'XLS File')], string='Select', default='xls')
	brand_id = fields.Many2one('product.brand', string="Brand", required=True)
	uom_id = fields.Many2one('product.uom', string="Product Uom", required=True)
	currency_id = fields.Many2one('res.currency', string="Currency", required=True, default=3)

	@api.multi
	def import_file(self):

# -----------------------------
		if self.import_option == 'csv':

			keys = ['default_code', 'name']

			try:
				csv_data = base64.b64decode(self.File_slect)
				data_file = io.StringIO(csv_data.decode("utf-8"))
				data_file.seek(0)
				file_reader = []
				values = {}
				csv_reader = csv.reader(data_file, delimiter=',')
				file_reader.extend(csv_reader)

			except:

				raise Warning(_("Invalid file!"))

			for i in range(len(file_reader)):
				field = list(map(str, file_reader[i]))
				values = dict(zip(keys, field))
				if values:
					if i == 0:
						continue
					else:
						values.update({
										'default_code' : field[0],
										'name' : field[1],
										'public_categ_ids' : field[2],
										})
						res = self.create_chart_products(values)

# ---------------------------------------
		elif self.import_option in ['xls', 'xlsx']:
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
					fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
				else:
					
					line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))

					values.update( {
						'default_code': str(line[0]),
						'name': str(line[1]),
						'name_eng': str(line[2]),
						'attribute_code': str(line[3]),
						'attribute_name': str(line[4]),
						'attribute_name_eng': str(line[5]),
						'attribute_value_code': str(line[6]),
						'attribute_value_name': str(line[7]),
						'attribute_value_name_eng': str(line[8]),
						'attribute_value_price': line[9],
						'attribute_required': line[10],
						'attribute_multi': line[11],
						'list_price': line[12],
						'sale_delay': line[13],
						})

					res = self.create_chart_products(values)
# ------------------------------------------------------------						
		else:
			raise Warning(_("Please select any one from xls or csv formate!"))

		return res
	@api.multi
	def create_chart_products(self, values):

		if values.get("default_code") == "" or not values.get("default_code"):
			raise Warning(_('Code field cannot be empty.'))

		if values.get("name") == "" or not values.get("name"):
			raise Warning(_('Name Field cannot be empty.'))

		if values.get("attribute_code") == "" or not values.get("attribute_code"):
			raise Warning(_('attribute_code field cannot be empty.'))

		if values.get("attribute_name") == "" or not values.get("attribute_name"):
			raise Warning(_('attribute_name field cannot be empty.'))

		if values.get("attribute_value_code") == "" or not values.get("attribute_value_code"):
			raise Warning(_('attribute_value_code field cannot be empty.'))

		if values.get("attribute_value_name") == "" or not values.get("attribute_value_name"):
			raise Warning(_('attribute_value_name field cannot be empty.'))

#		attribute_values = values.get("attribute_value").split(',')

		product_obj = self.env['product.template']
		product_tmpl = product_obj.search([
			('default_code', '=', values.get('default_code'))
			])
		if not product_tmpl:
			product_tmpl = self.env['product.template'].create({
				'name': values.get('name'),
				'default_code': values.get('default_code'),
				'list_price': values.get('list_price'),
				'sale_delay': values.get('sale_delay'),
				'type': 'product',
				'uom_id': self.uom_id.id,
				'product_brand_id': self.brand_id.id,
				'force_currency_id': self.currency_id.id,
				'tracking': 'serial',
				'config_ok': True,
			})
			product_tmpl.with_context(lang='en_US').write({'name': values.get('name_eng')})

		else:
			product_tmpl.write({'config_ok': True, 'list_price': values.get('list_price')})

		attrib_name = self.env['product.attribute'].search([('code', '=', values.get('attribute_code')), ('active', '=', True)])
		if not attrib_name:
			attrib_name = self.env['product.attribute'].create({
				'name': values.get('attribute_name'),
				'code': values.get('attribute_code'),
				'active': True
			})
			attrib_name.with_context(lang='en_US').write({'name': values.get('attribute_name_eng')})

		orj_attrib_value = self.env['product.attribute.value'].search(
			[('code', '=', values.get('attribute_value_code')), ('attribute_id', '=', attrib_name.id), ('active', '=', True)])

		if not orj_attrib_value:
			orj_attrib_value = self.env['product.attribute.value'].create({
							'name': values.get('attribute_value_name'),
							'code': values.get('attribute_value_code'),
							'active': True,
							'attribute_id': attrib_name.id,
						})
			orj_attrib_value.with_context(lang='en_US').write({'name': values.get('attribute_value_name_eng')})
		else:
			product_attribute_price = self.env['product.attribute.price'].search([('product_tmpl_id', '=', product_tmpl.id), ('value_id', '=', orj_attrib_value.id)])
			product_attribute_price.write({
				'price_extra': values.get('attribute_value_price'),
			})

		product_attribute_lines = product_tmpl.mapped('attribute_line_val_ids').filtered(lambda x: x.id == orj_attrib_value.id)

		if not product_attribute_lines:
			product_attribute_line_id = product_tmpl.mapped('attribute_line_ids').filtered(lambda x: x.code == attrib_name.code)
			if product_attribute_line_id:
				product_tmpl.write({'attribute_line_ids': [
					(1, product_attribute_line_id.id, {'value_ids': [(4, orj_attrib_value.id)], 'code': attrib_name.code})]})
			else:
				product_tmpl.update({
					'attribute_line_ids': [(0, 0, {
						'attribute_id': attrib_name.id,
						'code': attrib_name.code,
						'required': values.get('attribute_required'),
						'multi': values.get('attribute_multi'),
						'value_ids': [(4, orj_attrib_value.id)],
					})]
				})

			self.env['product.attribute.price'].create({
				'price_extra': values.get('attribute_value_price'),
				'product_tmpl_id': product_tmpl.id,
				'value_id': orj_attrib_value.id
			})

