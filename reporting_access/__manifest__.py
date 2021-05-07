# Copyright 2020 Pharmasimple (https://www.pharmasimple.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Reporting access",
    "category": "reporting_access_category",
    "summary": "Access to reporting menu of sales and ",
    "version": "14.0.1.0.0",
    "author": "Pharmasimple",
    "license": "AGPL-3",
    "website": "https://github.com/akretion/phs-addons",
    "depends": [
        "sale",
        "stock",
    ],
    "data": [
        "data/reporting_access.xml",
        "security/reporting_access_security.xml",
        "security/ir.model.access.csv",
        "views/reporting_access_menu.xml",
    ],
    "installable": True,
    "application": False,
}
