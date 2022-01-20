# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Phs Sale Channel",
    "summary": "Customisation for the e-commerce sale channel",
    "version": "14.0.1.0.0",
    "category": "Custom",
    "website": "https://github.com/akretion/phs-addons",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "sale_channel_hook_delivery_done",
    ],
    "data": [
        "views/sale_order_views.xml",
    ],
    "demo": [],
    "qweb": [],
}
