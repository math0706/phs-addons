{
    "name": "Product Refund",
    "summary": "Phs custom for shopinvader",
    "version": "14.0.1.0.0",
    "category": "custom",
    "website": "",
    "author": "Pharmasimple",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": ["stock"],
    "data": [
        "data/refund_request.xml",
        "views/sale_refund_request_views.xml",
        "views/stock_picking_views.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
}
