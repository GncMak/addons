# -*- coding: utf-8 -*-
{
	'name': 'Import Chart of Journal Items from CSV or Excel File',
	'summary': 'This apps helps to import chart of journal items using CSV or Excel file',
	'description': '''Using this module Charts os journal items is imported using excel sheets
	import journal items using csv 
	import journal items using xls
	import products using excel
	import Chart of journal items using csv 
	import Chart of journal items using xls
	import chart of journal items using excel
	import COA using csv 
	import COA using xls
	import COA using excel
	''',
	'author': 'BrowseInfo',	
	'website': 'https://www.browseinfo.in',
	'category': 'Account',
	'version': '11.0.0.3',
	'depends': ['base', 'account'],
	'data': [
		'security/ir.model.access.csv',
		'wizard/view_import_chart.xml',
		],
	'auto_install': False,
	'installable': True,
    'application': True,
    'qweb': [
    		],
    "images":['static/description/Banner.png']
}

