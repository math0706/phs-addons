from odoo.addons.component.core import Component


class LocationContentTransfer(Component):
    """"""

    _inherit = "shopfloor.location.content.transfer"

    def set_destination_line(
        self, location_id, move_line_id, quantity, barcode, confirmation=False
    ):
        res = super(LocationContentTransfer, self).set_destination_line(
            location_id, move_line_id, quantity, barcode, confirmation=False
        )

        putaway_rule = self.env["stock.putaway.rule"]
        company_id = self.env["res.company"].search([])
        loc_dest_id = self.env["stock.location"].search([("barcode", "=", barcode)])
        stock_move_id = self.env["stock.move.line"].browse(move_line_id).move_id
        product_id = stock_move_id.product_id
        putaway_rule_id = putaway_rule.search([("product_id", "=", product_id.id)])
        if not putaway_rule_id:
            putaway_rule.create(
                {
                    "product_id": product_id.id,
                    "location_in_id": location_id,
                    "location_out_id": loc_dest_id.id,
                    "company_id": company_id.id,
                }
            )

        return res
