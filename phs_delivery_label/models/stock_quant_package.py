from odoo import fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    parcel_tracking = fields.Char("Parcel Tracking")
    package_carrier_type = fields.Selection(
        related="packaging_id.package_carrier_type",
        string="Packaging's Carrier",
    )
