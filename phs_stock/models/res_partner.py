# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    def _compute_stock_orderpoint(self):
        for partner in self:
            orderpoint = self.domain_stock_orderpoint(True, partner)
            partner.stock_orderpoint_count = len(orderpoint)

    stock_orderpoint_count = fields.Integer(
        compute="_compute_stock_orderpoint", string="Stock Orderpoint"
    )

    def domain_stock_orderpoint(self, qty_to_order, partner_id):
        oderpoint = self.env["stock.warehouse.orderpoint"]
        product_supplier_info = self.env["product.supplierinfo"]
        product_supplier_info = product_supplier_info.search(
            [("name.id", "=", partner_id.id)]
        )
        domain = [
            (
                "product_tmpl_id.id",
                "in",
                product_supplier_info.mapped("product_tmpl_id.id"),
            )
        ]
        if qty_to_order:
            domain.append(("qty_to_order", ">", 0))
        orderpoint = oderpoint.search(domain)
        return orderpoint

    def stock_orderpoint(self):
        orderpoint = self.domain_stock_orderpoint(False, self)

        if orderpoint:
            return {
                "view_type": "tree",
                "view_mode": "tree",
                "res_model": "stock.warehouse.orderpoint",
                "domain": [("product_id", "in", orderpoint.mapped("product_id").ids)],
                "context": {"search_default_filter_to_reorder": 1},
                "type": "ir.actions.act_window",
            }
