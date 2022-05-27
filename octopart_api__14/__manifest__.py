{
    "name": "Octopart API",
    "version": "0.1",
    "summary": "Links product with Octopart",
    "author": "Norair Arutshyan",
    "depends": [
        "base",
        'web',
        "stock",
        "product",
        "mrp",
        "resource",
        "mail"
    ],
    'assets': {
        'web.assets_backend': [
            "octopart_api/static/src/js/*.js",
            "octopart_api/static/src/scss/*.scss",
            "octopart_api/static/src/xml/*.xml",
        ],
    },
    'application': True,
    'data': [
        "security/ir.model.access.csv",
        "views/octopart_parts_view.xml",
        "views/octopart_availability_view.xml",
        "views/octopart_manufacturers_view.xml",
        "views/octopart_vendors_view.xml",
        "views/product_views.xml",
        "report/mrp_report_bom_octopart_structure.xml",
        "views/mrp_production_views.xml",
        "views/mrp_bom_octopart_views.xml",
        "views/octopart_templates.xml",
        "views/octopart_settings_view.xml",
        "views/octopart_menu.xml",

    ],
    'qweb': ['static/src/xml/*.xml'],
    'license': 'LGPL-3',

}
