{
    "name": "Octopart Connector MRP",
    "version": "0.1",
    "summary": "Manufacturing order shows octopart linked parts in BOM and checkes if there is stock availability for it",
    "author": "Norair Arutshyan",
    "depends": [
        "octopart_connector",
        "mrp",
        "resource",
        "mail"
    ],
    'application': False,
    'data': [
        "security/ir.model.access.csv",
        "views/mrp_production_views.xml",


    ],
    'qweb': ['static/src/xml/*.xml'],
    'images': [
      'static/description/thumbnail.png',
  ],
}
