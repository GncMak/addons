{
    'name': "Konien Portal Stock Quants",
    'summary': """
        Lists product quantities and upcoming products on the portal page""",
    'author': "Konien Yazılım ve Danışmanlık Dış Tic. Ltd. Şti.",
    'website': "https://www.konien.com",
    'category': 'Stock',
    "version": "11.0.1.0.0",
    "license": "OPL-1",
    'depends': ['portal', 'stock'],
    'data': [
        'views/res_partner_views.xml',
        'views/quants_templates.xml',
        'views/product_templates.xml',
        'views/res_config_settings_views.xml',
        'security/ir.model.access.csv'
    ],
    'demo': [],
    'price': 49,
    'currency': 'EUR',
    'support': 'serkans@konien.com'
}
