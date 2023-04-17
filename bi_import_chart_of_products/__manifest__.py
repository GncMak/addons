# -*- coding: utf-8 -*-
{
	'name': 'Import Chart of Products from CSV or Excel File',
	'summary': 'This apps helps to import chart of products using CSV or Excel file',
	'description': '''Using this module Charts os products is imported using excel sheets
	import products using csv 
	import products using xls
	import products using excel
	import Chart of product using csv 
	import Chart of product using xls
	import chart of products using excel
	import COA using csv 
	import COA using xls
	import COA using excel
	''',
	'author': 'BrowseInfo',	
	'website': 'https://www.browseinfo.in',
	'category': 'Product',
	'version': '11.0.0.3',
	'depends': ['base','stock'],
	'data': [
		'security/ir.model.access.csv',
		'wizard/view_import_chart.xml',
		],
	'auto_install': False,
	'installable': True,
	'live_test_url'	:'https://youtu.be/ONRtviwfs1s',
    'application': True,
    'qweb': [
    		],
    "images":['static/description/Banner.png']
}

