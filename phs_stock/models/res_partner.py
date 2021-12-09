# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    def _compute_stock_orderpoint(self):
        for partner in self:
            stock = self.env["stock.warehouse.orderpoint"]
            stock = stock.search(
                [("supplier_id.id", "=", self.id), ("qty_to_order", ">", 0)]
            )
            partner.stock_orderpoint = len(stock)

    stock_orderpoint = fields.Integer(
        compute="_compute_stock_orderpoint", string="Stock Orderpoint"
    )
