{
    "name": "Octopart API",
    "version": "0.1",
    "summary": "Module to link parts with octopart",
    "author": "Norair Arutshyan",
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
    'license': 'LGPL-3',

}
