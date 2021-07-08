from odoo import fields, models


class CarrierAccount(models.Model):
    _inherit = "carrier.account"

    api_key = fields.Char()
    api_url = fields.Char()
    wt_carrierid = fields.Char()
    wt_providerservice_code = fields.Char()


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    is_welcometrack = fields.Boolean()
    carrier_account_id = fields.Many2one(comodel_name="carrier.account")
    sender_id = fields.Many2one(comodel_name="res.partner")
