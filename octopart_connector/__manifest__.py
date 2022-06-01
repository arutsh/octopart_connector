{
    "name": "Octopart Connector",
    "version": "1",
    "summary": "Module links products with octopart component name and check stock availability",
    "author": "Norair Arutshyan",
    'category': 'Inventory',
    'website': 'http://www.toolkit.tools/',
    "depends": [
        "base",
        'web',
        "stock",
        "product",
        "resource",
        "mail"
    ],

    'application': True,
    'data': [
        "security/ir.model.access.csv",
        "views/octopart_parts_view.xml",
        "views/octopart_availability_view.xml",
        "views/octopart_manufacturers_view.xml",
        "views/octopart_vendors_view.xml",
        "views/product_views.xml",
        "views/octopart_settings_view.xml",
        "views/octopart_menu.xml",

    ],
    'qweb': ['static/src/xml/*.xml'],
    'images': [
      'static/description/thumbnail.png',
    ],
    'license': 'LGPL-3',

}
