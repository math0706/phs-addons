# Copyright 2020 Pharmasimple (https://www.pharmasimple.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Product Auto Tags",
    "summary": """This module allow to set and unset automatically tags
        (new,top100delivered) on products
    """,
    "version": "14.0.1.0.0",
    "category": "Product",
    "website": "https://github.com/akretion/phs-addons",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "product",
        "product_template_tags",
    ],
    "data": [
        "data/ir_cron_data.xml",
        "data/product_template_data.xml",
    ],
    "demo": [],
    "qweb": [],
}
