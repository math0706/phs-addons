# Copyright 2020 Pharmasimple (https://www.pharmasimple.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Base delivery rate type",
    "category": "Inventory/Delivery",
    "summary": """Extend base Delivery module
    to split the delivery_type delivery_type an rate_type""",
    "version": "14.0.1.0.0",
    "author": "Pharmasimple",
    "license": "AGPL-3",
    "website": "https://github.com/akretion/phs-addons",
    "depends": [
        "delivery",
    ],
    "data": ["views/delivery_carrier.xml"],
    "installable": True,
    "application": False,
}
