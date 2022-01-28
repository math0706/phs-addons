# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[("mondialrelay", "Mondial Relay")],
        ondelete={"mondialrelay": "set default"},
    )
