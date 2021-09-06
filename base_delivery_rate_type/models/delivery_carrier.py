from odoo import api, fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    rate_type = fields.Selection(
        [
            ("fixed", "Fixed Price"),
            ("base_on_rule", "Based on Rules"),
        ],
        string="Rate type",
        default="fixed",
        required=True,
    )

    @api.onchange("delivery_type")
    def _onchange_user_type_id(self):
        if self.delivery_type in ["fixed", "base_on_rule"]:
            self.rate_type = False
        else:
            self.rate_type = "fixed"

    def welcometrack_rate_shipment(self, order):
        if self.rate_type == "fixed":
            return self.fixed_rate_shipment(order)
        if self.rate_type == "base_on_rule":
            return self.base_on_rule_rate_shipment(order)

    def welcometrack_send_shipping(self, pickings):
        if self.rate_type == "fixed":
            return self.fixed_send_shipping(pickings)
        if self.rate_type == "base_on_rule":
            return self.base_on_rule_send_shipping(pickings)

    def welcometrack_get_tracking_link(self, picking):
        return False

    def welcometrack_cancel_shipment(self, pickings):
        raise NotImplementedError()
