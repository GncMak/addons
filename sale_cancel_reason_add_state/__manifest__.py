# -*- coding: utf-8 -*-

{
    'name': 'Sale Cancel Reason Add State',
    'version': '10.0.1',
    'author': 'Camptocamp, Odoo Community Association',
    'category': 'Sale',
    'license': 'AGPL-3',
    'complexity': 'normal',
    'website': 'http://www.camptocamp.com',
    'summary': 'Add sale cancellation reason',
    'description': '''
        Sale Cancel Reason Add State
        ==================
        When a sale order is canceled, a reason must be given,
        it is chosen from a configured list. ''',
    'depends': ['sale', 'sale_cancel_reason'],
    'auto_install': False,
    'installable': True,
}
