# Copyright 2013-2016 Camptocamp SA
# Copyright 2014 Akretion <http://www.akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShippingLabelErrorLog(models.Model):
    _name = "shipping.label.error.log"
    _description = "Shipping Label error Log"

    address_diff = fields.Text()
    message = fields.Text(required=True)
    picking_id = fields.Many2one(comodel_name="stock.picking", required=True)
    log_type = fields.Selection(
        selection=[
            ("error", "Error"),
            ("fix", "Resolution"),
        ]
    )
