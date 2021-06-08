# Copyright 2020 Pharmasimple (https://www.pharmasimple.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Product Editor",
    "category": "Custom",
    "summary": """
    Product Editor
    ==================
    This module adds a group *Product Editor Manager* to allow the manager to update products
    """,
    "version": "14.0.1.0.0",
    "author": "Pharmasimple",
    "license": "AGPL-3",
    "website": "https://github.com/akretion/phs-addons",
    "depends": ["base", "product"],
    "data": [
        "security/product_security.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
