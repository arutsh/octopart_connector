{
    "name": "Octopart Connector MRP Cost structure",
    "version": "0.1",
    "summary": "Enhances BOM cost and structure and shows Min, Max and Avg cost of the BOM",
    "author": "Norair Arutshyan",
    'website': 'http://www.toolkit.tools/',
    'category': 'MRP',
    "depends": [
        "octopart_connector"
    ],

    'data': [
        "security/ir.model.access.csv",
        "report/mrp_report_bom_octopart_structure.xml",
        "views/mrp_bom_octopart_views.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'octopart_connector_cost/static/src/js/mrp_bom_report_octopart.js',

        ],
        'web.assets_common': [
            'octopart_connector_cost/static/src/scss/mrp_workorder_kanban.scss',
        ],
        'web.assets_qweb': [
            'octopart_connector_cost/static/src/xml/*.xml',
        ],
    },

    'qweb': ['static/src/xml/*.xml'],
    'images': [
      'static/description/thumbnail.png',
      ],
      'license': 'LGPL-3',
}
