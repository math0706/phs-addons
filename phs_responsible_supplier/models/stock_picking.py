from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    responsible_supplier_id = fields.Many2one(
        string="Responsible Supplier",
        comodel_name="res.partner",
        related="partner_id.responsible_supplier_id",
    )
