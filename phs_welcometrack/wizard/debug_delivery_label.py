import json

from odoo import api, fields, models


class DebugDeliveryLabel(models.TransientModel):
    _name = "debug.delivery.label"
    _description = (
        "Wizard to debug label creation with delivery address correction if needed"
    )

    @api.onchange("picking_id")
    def _onchange_move_id(self):
        if self.picking_id:
            address = self.picking_id.partner_id
            self.name = address.name
            self.street = address.street
            self.street2 = address.street2
            self.zip = address.zip
            self.city = address.city
            self.state_id = address.state_id
            self.country_id = address.country_id
            self.email = address.email
            self.phone = address.phone
            self.mobile = address.mobile
            self.substitution_carrier_id = self.picking_id.carrier_id.id
            self.error = True

    @api.onchange(
        "name",
        "street",
        "street2",
        "zip",
        "city",
        "state_id",
        "country_id",
        "email",
        "phone",
        "mobile",
    )
    def _onchange_update_error(self):
        self.error = True

    # address fields
    picking_id = fields.Many2one(comodel_name="stock.picking", required=True)
    carrier_id = fields.Many2one(related="picking_id.carrier_id", readonly=True)
    substitution_carrier_id = fields.Many2one(
        comodel_name="delivery.carrier", string="Substitution carrier"
    )
    name = fields.Char()
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one(
        comodel_name="res.country.state",
        string="State",
        domain="[('country_id', '=?', country_id)]",
    )
    country_id = fields.Many2one(comodel_name="res.country", string="Country")
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()
    error = fields.Boolean()
    message = fields.Text()
    payload = fields.Text()

    def action_check_label(self):
        check = True
        labels = self.picking_id._generate_shipping_labels(
            check, self, self.substitution_carrier_id
        )
        self.payload = json.dumps(labels["payload"], sort_keys=False, indent=2)
        self.message = json.dumps(labels["error_message"], sort_keys=False, indent=2)
        if labels["error_message"] is not None:
            self.error = True
        else:
            self.error = False
        action = self.env["ir.actions.actions"]._for_xml_id(
            "phs_welcometrack.debug_delivery_label_action"
        )

        action["res_id"] = self.id

        return action

    def action_print_label(self):
        diff = []
        for field in [
            "name",
            "street",
            "street2",
            "zip",
            "city",
            "state_id",
            "country_id",
            "email",
            "phone",
            "mobile",
        ]:
            if self.picking_id.partner_id[field] != self[field]:
                diff.append(f"Diff in {field}")
                diff.append(f"{self.picking_id.partner_id[field]} <> {self[field]}")
        diff = "\n".join(diff)
        self.env["shipping.label.error.log"].create(
            {"picking_id": self.picking_id.id, "log_type": "fix", "message": diff}
        )

        self.picking_id.partner_id.sudo().write(
            {
                "name": self.name,
                "street": self.street,
                "street2": self.street2,
                "zip": self.zip,
                "city": self.city,
                "state_id": self.state_id,
                "country_id": self.country_id,
                "email": self.email,
                "phone": self.phone,
                "mobile": self.mobile,
            }
        )

        if self.picking_id.carrier_id.id != self.substitution_carrier_id.id:
            self.picking_id.carrier_id = self.substitution_carrier_id.id

        self.picking_id.send_to_shipper()

        return {"type": "ir.actions.act_window_close"}
