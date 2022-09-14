# -*- coding: utf-8 -*-
# Copyright 2020 Konien Ltd.Şti.
{
    'name': "Bulut Tahsilat Account Bank Statement Integration",
    'summary': """
        Bulut Tahsilat Account Bank Statement Integration""",
    'author': "Konien Yazılım ve Danışmanlık Ltd. Şti.",
    "website": "https://www.konien.com",
    'category': 'account',
    "version": "11.0.1",
    'depends': ['account'],
    'external_dependencies': {'python': ['phonenumbers', 'suds']},
    'data': [
        'security/ir.model.access.csv',
        'security/bulut_service_security.xml',
        'views/res_company.xml',
        'views/res_partner.xml',
        'views/bulut_tahsilat_service.xml',
        'views/bank_statement.xml',
        'views/account_journal.xml',
        'views/product_template.xml',
        'views/account_payment.xml',
        'views/account_invoice.xml',
        'views/partner_bank.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
