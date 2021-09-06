from odoo import fields, models


class CarrierAccount(models.Model):
    _inherit = "carrier.account"

    api_key = fields.Char()
    api_url = fields.Char()
    wt_carrierid = fields.Char()
    wt_providerservice_code = fields.Char()


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[
            ("welcometrack", "Welcometrack"),
        ],
        ondelete={
            "welcometrack": lambda recs: recs.write(
                {
                    "delivery_type": "fixed",
                    "fixed_price": 0,
                }
            )
        },
    )
    is_welcometrack = fields.Boolean(default=False)
    carrier_account_id = fields.Many2one(comodel_name="carrier.account")
    sender_id = fields.Many2one(comodel_name="res.partner")
