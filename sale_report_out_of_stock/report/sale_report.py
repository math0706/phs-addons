from odoo import api, models


class SaleReportSaleOrder(models.AbstractModel):
    _name = "report.sale.report_saleorder"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["sale.order"].browse(docids)
        stock = self.env["stock.location"].search(
            [("name", "=", "Stock"), ("location_id.name", "=", "WHDV")]
        )
        move_ids = self.env["stock.picking"].search(
            [("origin", "=", docs.name), ("location_id", "=", stock.id)]
        )
        not_in_stock = []
        ok = True
        for move in move_ids.move_ids_without_package:
            if move.reserved_availability < move.product_uom_qty:
                ok = False
            not_in_stock.append({"name": move.product_id.name, "in_stock": ok})
            ok = True

        return {
            "doc_ids": docs.ids,
            "stock_list": not_in_stock,
            "doc_model": "sale.order",
            "docs": docs,
            "proforma": True,
        }
