# Copyright 2020 Pharmasimple (https://www.pharmasimple.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Phs Stock Custo",
    "category": "Custom",
    "summary": "Stock customisation",
    "version": "14.0.1.0.0",
    "author": "Akretion",
    "license": "AGPL-3",
    "website": "https://github.com/akretion/phs-addons",
    "depends": [
        # "stock",
        "product",
        "stock_picking_batch",
        "shopfloor",
    ],
    "data": [
        "wizard/batch_force_create_view.xml",
        "views/res_partner_views.xml",
        "views/product_category.xml",
        "views/stock_picking_batch.xml",
        "views/stock_picking_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": False,
}
