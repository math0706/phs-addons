# Copyright 2020 Pharmasimple (https://www.pharmasimple.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Reception Error",
    "category": "Stock",
    "summary": "Stock Reception Error",
    "version": "14.0.1.0.0",
    "author": "Pharmasimple",
    "license": "AGPL-3",
    "website": "https://github.com/akretion/phs-addons",
    "depends": ["mail", "stock", "purchase"],
    "data": [
        "data/stock_reception_error.xml",
        "security/ir.model.access.csv",
        "views/stock_reception_error.xml",
    ],
    "installable": True,
    "application": False,
}
