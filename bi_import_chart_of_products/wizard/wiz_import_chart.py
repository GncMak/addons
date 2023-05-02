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
	product_type = fields.Many2one('product.product.type', string="Product Type", required=True)

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
						'attribute_active': str(line[3]),
                        'attribute_code': str(line[4]),
						'attribute_name': str(line[5]),
						'attribute_name_eng': str(line[6]),
                        'attribute_value_active': str(line[7]),
						'attribute_value_code': str(line[8]),
						'attribute_value_name': str(line[9]),
						'attribute_value_name_eng': str(line[10]),
						'attribute_value_price': line[11],
						'attribute_required': line[12],
						'attribute_multi': line[13],
						'list_price': line[14],
						'sale_delay': line[15],
                        'mensei': line[16],
                        'gtip': line[17],
                        'manufacturer': line[18],
                        'main_category': line[19],
                        'main_category_definition': line[20],
                        'sub_category': line[21],
                        'sub_category_definition': line[22],
                        'mechanic_warranty': line[23],
                        'control_unit_warranty': line[24],
                        'purchase_discount': line[25],
                        'gross_profit': line[26],
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

		if values.get("attribute_active") == "" or not values.get("attribute_active"):
			raise Warning(_('Attribute active field cannot be empty.'))

		if values.get("attribute_value_active") == "" or not values.get("attribute_value_active"):
			raise Warning(_('Attribute value active field cannot be empty.'))

		if values.get("main_category") == "" or not values.get("main_category"):
			raise Warning(_('Main category field cannot be empty.'))

		if values.get("main_category_definition") == "" or not values.get("main_category_definition"):
			raise Warning(_('Main category definition field cannot be empty.'))

		if values.get("sub_category") == "" or not values.get("sub_category"):
			raise Warning(_('sub category field cannot be empty.'))

		if values.get("sub_category_definition") == "" or not values.get("sub_category_definition"):
			raise Warning(_('Sub category definition field cannot be empty.'))

		if values.get("purchase_discount") == "" or not values.get("purchase_discount"):
			raise Warning(_('Purchase discount field cannot be empty.'))

		if values.get("gross_profit") == "" or not values.get("gross_profit"):
			raise Warning(_('Gross profit field cannot be empty.'))

#		attribute_values = values.get("attribute_value").split(',')


#purchase_discount
#gross_profit


		country_id = self.env['res.country'].search([('name', '=', values.get('mensei'))])
		if not country_id:
			country_id = self.env['res.country'].create({'name': values.get('mensei')})

		manufacturer_id = self.env['res.partner'].search([('name', '=', values.get('manufacturer'))])
		if not manufacturer_id:
			manufacturer_id = self.env['res.partner'].create({'name': values.get('manufacturer')})

		main_category = self.env['x_main_category'].search([('x_name', '=', values.get('main_category'))])
		if not main_category:
			main_category = self.env['x_main_category'].create({'x_name': values.get('main_category'),'x_studio_field_151WL': '99'})

		main_category_definition = self.env['x_main_category_definition'].search([('x_name', '=', values.get('main_category_definition')),('x_studio_field_j5lhE', '=', main_category.id)])
		if not main_category_definition:
			main_category_definition = self.env['x_main_category_definition'].create({'x_name': values.get('main_category_definition'), 'x_studio_field_H40pY': '99','x_studio_field_j5lhE': main_category.id})

		sub_category = self.env['x_sub_category'].search([('x_name', '=', values.get(
            'sub_category')), ('x_studio_field_B0Urb', '=', main_category_definition.id)])
		if not sub_category:
			sub_category = self.env['x_sub_category'].create({'x_name': values.get('sub_category'), 'x_studio_field_SjpPe': '99', 'x_studio_field_B0Urb': main_category_definition.id})

		sub_category_definition = self.env['x_sub_category_definition'].search([('x_name', '=', values.get(
            'sub_category_definition')), ('x_studio_field_NGvMM', '=', sub_category.id)])
		if not sub_category_definition:
			sub_category_definition = self.env['x_sub_category_definition'].create(
                {'x_name': values.get('sub_category_definition'), 'x_studio_field_iygol': '99',
                 'x_studio_field_NGvMM': sub_category.id})

		sale_pricelist_maliyet_usd = self.env['product.pricelist'].search([('name', '=', '[Maliyet] Fiyat Listesi'),
															   ('currency_id.name', '=', 'USD'),
															   ('company_id', '=', False)
															   ])
		sale_pricelist_maliyet_try = self.env['product.pricelist'].search([('name', '=', '[Maliyet] Fiyat Listesi'),
																		   ('currency_id.name', '=', 'TRY'),
																		   ('company_id', '=', False)
																		   ])
		sale_pricelist_maliyet_gbp = self.env['product.pricelist'].search([('name', '=', '[Maliyet] Fiyat Listesi'),
																		   ('currency_id.name', '=', 'GBP'),
																		   ('company_id', '=', False)
																		   ])
		sale_pricelist_maliyet_eur = self.env['product.pricelist'].search([('name', '=', '[Maliyet] Fiyat Listesi'),
																		   ('currency_id.name', '=', 'EUR'),
																		   ('company_id', '=', False)
																		   ])
		sale_pricelist_maliyet_jpy = self.env['product.pricelist'].search([('name', '=', '[Maliyet] Fiyat Listesi'),
																		   ('currency_id.name', '=', 'JPY'),
																		   ('company_id', '=', False)
																		   ])
		sale_pricelist_satis_usd = self.env['product.pricelist'].search([('name', '=', '[Satış] Fiyat Listesi'),
																		 ('currency_id.name', '=', 'USD'),
																		 ('company_id', '=', False)
																		 ])
		sale_pricelist_satis_try = self.env['product.pricelist'].search([('name', '=', '[Satış] Fiyat Listesi'),
																		 ('currency_id.name', '=', 'TRY'),
																		 ('company_id', '=', False)
																		 ])
		sale_pricelist_satis_gbp = self.env['product.pricelist'].search([('name', '=', '[Satış] Fiyat Listesi'),
																		 ('currency_id.name', '=', 'GBP'),
																		 ('company_id', '=', False)
																		 ])
		sale_pricelist_satis_eur = self.env['product.pricelist'].search([('name', '=', '[Satış] Fiyat Listesi'),
																		 ('currency_id.name', '=', 'EUR'),
																		 ('company_id', '=', False)
																		 ])
		sale_pricelist_satis_jpy = self.env['product.pricelist'].search([('name', '=', '[Satış] Fiyat Listesi'),
																		 ('currency_id.name', '=', 'JPY'),
																		 ('company_id', '=', False)
																		 ])

		product_tmpl = self.env['product.template'].search([
			('default_code', '=', values.get('default_code'))
			])
		if not product_tmpl:
			product_tmpl = self.env['product.template'].create({
				'name': values.get('name'),
				'default_code': values.get('default_code'),
				'list_price': float(values.get('list_price')),
				'sale_delay': values.get('sale_delay'),
				'type': 'product',
                'product_type': self.product_type.id,
				'uom_id': self.uom_id.id,
                'uom_po_id': self.uom_id.id,
				'product_brand_id': self.brand_id.id,
				'force_currency_id': self.currency_id.id,
				'tracking': 'serial',
				'config_ok': True,
                'origin_country_id': country_id.id,
                'hs_code': values.get('gtip'),
                'manufacturer': manufacturer_id.id,
                'x_studio_field_ZFEDs': main_category.id,
                'x_studio_field_rffrE': main_category_definition.id,
                'x_studio_field_DxdDi': sub_category.id,
                'x_studio_field_M7hSn': sub_category_definition.id,
                'x_studio_field_NWylj': values.get('mechanic_warranty'),
                'x_warranty_control': values.get('control_unit_warranty')
			})
			product_tmpl.with_context(lang='en_US').write({'name': values.get('name_eng')})
			vendor = self.env['product.supplierinfo'].create(
				{'product_tmpl_id': product_tmpl.id,
				 'name': manufacturer_id.id,
				 'delay': 1,
				 'min_qty': 0,
				 'currency_id': self.currency_id.id,
				 'price': float(values.get('list_price')) * (1 - (float(values.get('purchase_discount')) / 100))
				 })

			if not sale_pricelist_maliyet_usd:
				raise Warning(_('[Maliyet] Fiyat Listesi isminde ve Usd döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat lsitesi tanımını yapınız.'))
			else:
				self.env['product.pricelist.item'].create(
					{'applied_on': '1_product',
					 'product_tmpl_id': product_tmpl.id,
					 'compute_price': 'formula',
					 'base': 'list_price',
					 'pricelist_id': sale_pricelist_maliyet_usd.id,
					 'price_discount': float(values.get('purchase_discount')),
					 'min_quantity': 0
					 })

			if not sale_pricelist_maliyet_try:
				raise Warning(_('[Maliyet] Fiyat Listesi isminde ve try döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat lsitesi tanımını yapınız.'))
			else:
				self.env['product.pricelist.item'].create(
					{'applied_on': '1_product',
					 'product_tmpl_id': product_tmpl.id,
					 'compute_price': 'formula',
					 'base': 'list_price',
					 'pricelist_id': sale_pricelist_maliyet_try.id,
					 'price_discount': float(values.get('purchase_discount')),
					 'min_quantity': 0
					 })

			if not sale_pricelist_maliyet_gbp:
				raise Warning(_('[Maliyet] Fiyat Listesi isminde ve gbp döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat lsitesi tanımını yapınız.'))
			else:
				self.env['product.pricelist.item'].create(
					{'applied_on': '1_product',
					 'product_tmpl_id': product_tmpl.id,
					 'compute_price': 'formula',
					 'base': 'list_price',
					 'pricelist_id': sale_pricelist_maliyet_gbp.id,
					 'price_discount': float(values.get('purchase_discount')),
					 'min_quantity': 0
					 })

			if not sale_pricelist_maliyet_eur:
				raise Warning(_('[Maliyet] Fiyat Listesi isminde ve eur döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat lsitesi tanımını yapınız.'))
			else:
				self.env['product.pricelist.item'].create(
					{'applied_on': '1_product',
					 'product_tmpl_id': product_tmpl.id,
					 'compute_price': 'formula',
					 'base': 'list_price',
					 'pricelist_id': sale_pricelist_maliyet_eur.id,
					 'price_discount': float(values.get('purchase_discount')),
					 'min_quantity': 0
					 })

			if not sale_pricelist_maliyet_jpy:
				raise Warning(_('[Maliyet] Fiyat Listesi isminde ve jpy döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat lsitesi tanımını yapınız.'))
			else:
				self.env['product.pricelist.item'].create(
					{'applied_on': '1_product',
					 'product_tmpl_id': product_tmpl.id,
					 'compute_price': 'formula',
					 'base': 'list_price',
					 'pricelist_id': sale_pricelist_maliyet_jpy.id,
					 'price_discount': float(values.get('purchase_discount')),
					 'min_quantity': 0
					 })

			if not sale_pricelist_satis_usd:
				raise Warning(_('[Satış] Fiyat Listesi isminde ve usd döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat lsitesi tanımını yapınız.'))
			else:
				self.env['product.pricelist.item'].create(
					{'applied_on': '1_product',
					 'product_tmpl_id': product_tmpl.id,
					 'compute_price': 'formula',
					 'base': 'list_price',
					 'pricelist_id': sale_pricelist_satis_usd.id,
					 'price_discount': (-1) * float(values.get('gross_profit')),
					 'min_quantity': 0
					 })

			if not sale_pricelist_satis_try:
				raise Warning(_('[Satış] Fiyat Listesi isminde ve try döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat lsitesi tanımını yapınız.'))
			else:
				self.env['product.pricelist.item'].create(
					{'applied_on': '1_product',
					 'product_tmpl_id': product_tmpl.id,
					 'compute_price': 'formula',
					 'base': 'list_price',
					 'pricelist_id': sale_pricelist_satis_try.id,
					 'price_discount': (-1) * float(values.get('gross_profit')),
					 'min_quantity': 0
					 })

			if not sale_pricelist_satis_gbp:
				raise Warning(_('[Satış] Fiyat Listesi isminde ve gbp döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat lsitesi tanımını yapınız.'))
			else:
				self.env['product.pricelist.item'].create(
					{'applied_on': '1_product',
					 'product_tmpl_id': product_tmpl.id,
					 'compute_price': 'formula',
					 'base': 'list_price',
					 'pricelist_id': sale_pricelist_satis_gbp.id,
					 'price_discount': (-1) * float(values.get('gross_profit')),
					 'min_quantity': 0
					 })

			if not sale_pricelist_satis_eur:
				raise Warning(_('[Satış] Fiyat Listesi isminde ve eur döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat lsitesi tanımını yapınız.'))
			else:
				self.env['product.pricelist.item'].create(
					{'applied_on': '1_product',
					 'product_tmpl_id': product_tmpl.id,
					 'compute_price': 'formula',
					 'base': 'list_price',
					 'pricelist_id': sale_pricelist_satis_eur.id,
					 'price_discount': (-1) * float(values.get('gross_profit')),
					 'min_quantity': 0
					 })

			if not sale_pricelist_satis_jpy:
				raise Warning(_('[Satış] Fiyat Listesi isminde ve jpy döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat lsitesi tanımını yapınız.'))
			else:
				self.env['product.pricelist.item'].create(
					{'applied_on': '1_product',
					 'product_tmpl_id': product_tmpl.id,
					 'compute_price': 'formula',
					 'base': 'list_price',
					 'pricelist_id': sale_pricelist_satis_jpy.id,
					 'price_discount': (-1) * float(values.get('gross_profit')),
					 'min_quantity': 0
					 })
		else:
			product_tmpl.write({'config_ok': True, 'list_price': values.get('list_price')})
			if not sale_pricelist_maliyet_usd:
				raise Warning(_('[Maliyet] Fiyat Listesi isminde ve Usd döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat listesi tanımını yapınız.'))
			else:
				sale_pricelist_maliyet_usd_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', sale_pricelist_maliyet_usd.id),
																							 ('product_tmpl_id', '=', product_tmpl.id),
																							 ('compute_price', '=', 'formula'),
																							 ('base', '=', 'list_price'),
																							 ('applied_on', '=', '1_product')
																						 	])
				if sale_pricelist_maliyet_usd_item:
					sale_pricelist_maliyet_usd_item.write({'price_discount': float(values.get('purchase_discount'))})
				else:
					self.env['product.pricelist.item'].create({'applied_on': '1_product',
																		 'product_tmpl_id': product_tmpl.id,
																		 'compute_price': 'formula',
																		 'base': 'list_price',
																		 'pricelist_id': sale_pricelist_maliyet_usd.id,
																		 'price_discount': float(values.get('purchase_discount')),
																		 'min_quantity': 0
					 })

			if not sale_pricelist_maliyet_try:
				raise Warning(_('[Maliyet] Fiyat Listesi isminde ve Try döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat listesi tanımını yapınız.'))
			else:
				sale_pricelist_maliyet_try_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', sale_pricelist_maliyet_try.id),
																							 ('product_tmpl_id', '=', product_tmpl.id),
																							 ('compute_price', '=', 'formula'),
																							 ('base', '=', 'list_price'),
																							 ('applied_on', '=', '1_product')
																						 	])
				if sale_pricelist_maliyet_try_item:
					sale_pricelist_maliyet_try_item.write({'price_discount': float(values.get('purchase_discount'))})
				else:
					self.env['product.pricelist.item'].create({'applied_on': '1_product',
																		 'product_tmpl_id': product_tmpl.id,
																		 'compute_price': 'formula',
																		 'base': 'list_price',
																		 'pricelist_id': sale_pricelist_maliyet_try.id,
																		 'price_discount': float(values.get('purchase_discount')),
																		 'min_quantity': 0
					 })

			if not sale_pricelist_maliyet_gbp:
				raise Warning(_('[Maliyet] Fiyat Listesi isminde ve Gbp döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat listesi tanımını yapınız.'))
			else:
				sale_pricelist_maliyet_gbp_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', sale_pricelist_maliyet_gbp.id),
																							 ('product_tmpl_id', '=', product_tmpl.id),
																							 ('compute_price', '=', 'formula'),
																							 ('base', '=', 'list_price'),
																							 ('applied_on', '=', '1_product')
																						 	])
				if sale_pricelist_maliyet_gbp_item:
					sale_pricelist_maliyet_gbp_item.write({'price_discount': float(values.get('purchase_discount'))})
				else:
					self.env['product.pricelist.item'].create({'applied_on': '1_product',
																		 'product_tmpl_id': product_tmpl.id,
																		 'compute_price': 'formula',
																		 'base': 'list_price',
																		 'pricelist_id': sale_pricelist_maliyet_gbp.id,
																		 'price_discount': float(values.get('purchase_discount')),
																		 'min_quantity': 0
					 })

			if not sale_pricelist_maliyet_eur:
				raise Warning(_('[Maliyet] Fiyat Listesi isminde ve Eur döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat listesi tanımını yapınız.'))
			else:
				sale_pricelist_maliyet_eur_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', sale_pricelist_maliyet_eur.id),
																							 ('product_tmpl_id', '=', product_tmpl.id),
																							 ('compute_price', '=', 'formula'),
																							 ('base', '=', 'list_price'),
																							 ('applied_on', '=', '1_product')
																						 	])
				if sale_pricelist_maliyet_eur_item:
					sale_pricelist_maliyet_eur_item.write({'price_discount': float(values.get('purchase_discount'))})
				else:
					self.env['product.pricelist.item'].create({'applied_on': '1_product',
																		 'product_tmpl_id': product_tmpl.id,
																		 'compute_price': 'formula',
																		 'base': 'list_price',
																		 'pricelist_id': sale_pricelist_maliyet_eur.id,
																		 'price_discount': float(values.get('purchase_discount')),
																		 'min_quantity': 0
					 })

			if not sale_pricelist_maliyet_jpy:
				raise Warning(_('[Maliyet] Fiyat Listesi isminde ve Jpy döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat listesi tanımını yapınız.'))
			else:
				sale_pricelist_maliyet_jpy_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', sale_pricelist_maliyet_jpy.id),
																							 ('product_tmpl_id', '=', product_tmpl.id),
																							 ('compute_price', '=', 'formula'),
																							 ('base', '=', 'list_price'),
																							 ('applied_on', '=', '1_product')
																						 	])
				if sale_pricelist_maliyet_jpy_item:
					sale_pricelist_maliyet_jpy_item.write({'price_discount': float(values.get('purchase_discount'))})
				else:
					self.env['product.pricelist.item'].create({'applied_on': '1_product',
																'product_tmpl_id': product_tmpl.id,
																'compute_price': 'formula',
																'base': 'list_price',
																'pricelist_id': sale_pricelist_maliyet_jpy.id,
																'price_discount': float(values.get('purchase_discount')),
																'min_quantity': 0
																})

			if not sale_pricelist_satis_usd:
				raise Warning(_('[Satış] Fiyat Listesi isminde ve Usd döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat listesi tanımını yapınız.'))
			else:
				sale_pricelist_satis_usd_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', sale_pricelist_satis_usd.id),
																							 ('product_tmpl_id', '=', product_tmpl.id),
																							 ('compute_price', '=', 'formula'),
																							 ('base', '=', 'list_price'),
																							 ('applied_on', '=', '1_product')
																						 	])
				if sale_pricelist_satis_usd_item:
					sale_pricelist_satis_usd_item.write({'price_discount': (-1) * float(values.get('gross_profit'))})
				else:
					self.env['product.pricelist.item'].create({'applied_on': '1_product',
																		 'product_tmpl_id': product_tmpl.id,
																		 'compute_price': 'formula',
																		 'base': 'list_price',
																		 'pricelist_id': sale_pricelist_satis_usd.id,
																		 'price_discount': (-1) * float(values.get('gross_profit')),
																		 'min_quantity': 0
					 })

			if not sale_pricelist_satis_try:
				raise Warning(_('[Satış] Fiyat Listesi isminde ve Try döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat listesi tanımını yapınız.'))
			else:
				sale_pricelist_satis_try_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', sale_pricelist_satis_try.id),
																							 ('product_tmpl_id', '=', product_tmpl.id),
																							 ('compute_price', '=', 'formula'),
																							 ('base', '=', 'list_price'),
																							 ('applied_on', '=', '1_product')
																						 	])
				if sale_pricelist_satis_try_item:
					sale_pricelist_satis_try_item.write({'price_discount': (-1) * float(values.get('gross_profit'))})
				else:
					self.env['product.pricelist.item'].create({'applied_on': '1_product',
																		 'product_tmpl_id': product_tmpl.id,
																		 'compute_price': 'formula',
																		 'base': 'list_price',
																		 'pricelist_id': sale_pricelist_satis_try.id,
																		 'price_discount': (-1) * float(values.get('gross_profit')),
																		 'min_quantity': 0
					 })

			if not sale_pricelist_satis_gbp:
				raise Warning(_('[Satış] Fiyat Listesi isminde ve Gbp döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat listesi tanımını yapınız.'))
			else:
				sale_pricelist_satis_gbp_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', sale_pricelist_satis_gbp.id),
																							 ('product_tmpl_id', '=', product_tmpl.id),
																							 ('compute_price', '=', 'formula'),
																							 ('base', '=', 'list_price'),
																							 ('applied_on', '=', '1_product')
																						 	])
				if sale_pricelist_satis_gbp_item:
					sale_pricelist_satis_gbp_item.write({'price_discount': (-1) * float(values.get('gross_profit'))})
				else:
					self.env['product.pricelist.item'].create({'applied_on': '1_product',
																		 'product_tmpl_id': product_tmpl.id,
																		 'compute_price': 'formula',
																		 'base': 'list_price',
																		 'pricelist_id': sale_pricelist_satis_gbp.id,
																		 'price_discount': (-1) * float(values.get('gross_profit')),
																		 'min_quantity': 0
					 })

			if not sale_pricelist_satis_eur:
				raise Warning(_('[Satış] Fiyat Listesi isminde ve Eur döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat listesi tanımını yapınız.'))
			else:
				sale_pricelist_satis_eur_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', sale_pricelist_satis_eur.id),
																							 ('product_tmpl_id', '=', product_tmpl.id),
																							 ('compute_price', '=', 'formula'),
																							 ('base', '=', 'list_price'),
																							 ('applied_on', '=', '1_product')
																						 	])
				if sale_pricelist_satis_eur_item:
					sale_pricelist_satis_eur_item.write({'price_discount': (-1) * float(values.get('gross_profit'))})
				else:
					self.env['product.pricelist.item'].create({'applied_on': '1_product',
																		 'product_tmpl_id': product_tmpl.id,
																		 'compute_price': 'formula',
																		 'base': 'list_price',
																		 'pricelist_id': sale_pricelist_satis_eur.id,
																		 'price_discount': (-1) * float(values.get('gross_profit')),
																		 'min_quantity': 0
					 })

			if not sale_pricelist_satis_jpy:
				raise Warning(_('[Satış] Fiyat Listesi isminde ve Jpy döviz cinsinde fiyat listesi bulunamadı. Lütfen öncelikle fiyat listesi tanımını yapınız.'))
			else:
				sale_pricelist_satis_jpy_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', sale_pricelist_satis_jpy.id),
																							 ('product_tmpl_id', '=', product_tmpl.id),
																							 ('compute_price', '=', 'formula'),
																							 ('base', '=', 'list_price'),
																							 ('applied_on', '=', '1_product')
																						 	])
				if sale_pricelist_satis_jpy_item:
					sale_pricelist_satis_jpy_item.write({'price_discount': (-1) * float(values.get('gross_profit'))})
				else:
					self.env['product.pricelist.item'].create({'applied_on': '1_product',
																		 'product_tmpl_id': product_tmpl.id,
																		 'compute_price': 'formula',
																		 'base': 'list_price',
																		 'pricelist_id': sale_pricelist_satis_jpy.id,
																		 'price_discount': (-1) * float(values.get('gross_profit')),
																		 'min_quantity': 0
					 })

		attrib_name = self.env['product.attribute'].search([('code', '=', values.get('attribute_code')), ('active', '=', values.get('attribute_active'))])
		if not attrib_name:
			attrib_name = self.env['product.attribute'].create({
				'name': values.get('attribute_name'),
				'code': values.get('attribute_code'),
                'active': values.get('attribute_active')
			})
			attrib_name.with_context(lang='en_US').write({'name': values.get('attribute_name_eng')})

		orj_attrib_value = self.env['product.attribute.value'].search(
			[('code', '=', values.get('attribute_value_code')), ('attribute_id', '=', attrib_name.id), ('active', '=', values.get('attribute_value_active'))])

		if not orj_attrib_value:
			orj_attrib_value = self.env['product.attribute.value'].create({
							'name': values.get('attribute_value_name'),
							'code': values.get('attribute_value_code'),
							'active': values.get('attribute_value_active'),
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

