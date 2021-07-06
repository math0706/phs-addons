# Copyright 2020 Pharmasimple (https://www.pharmasimple.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Import From API",
    "category": "Custom",
    "summary": """
    """,
    "version": "14.0.1.0.0",
    "author": "Pharmasimple",
    "license": "AGPL-3",
    "website": "https://github.com/akretion/phs-addons",
    "depends": ["base", "product", "stock"],
    "external_dependencies": {
        "python": ["dictor"],
    },
    "data": [
        "security/ir.model.access.csv",
        "wizard/import_product_view.xml",
        "views/product_product_view.xml",
    ],
    "installable": True,
}
