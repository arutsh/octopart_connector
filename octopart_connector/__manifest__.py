{
    "name": "Octopart Connector",
    "version": "1.6",
    "summary":
    '''Module links products with octopart component name and check stock availability
    v1.5: changing module structure to general one, so in the future any octopart
    like API can be linked to system
    ''',
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
        "views/octopart_parts_history_view.xml",
        "views/octopart_vendors_view.xml",
        "views/octopart_settings_view.xml",
        "views/octopart_menu.xml",
        "views/product_views.xml",
        "views/products_history_view.xml",


    ],
    'qweb': ['static/src/xml/*.xml'],
    'images': [
      'static/description/thumbnail.png',
    ],
    'license': 'LGPL-3',

}
