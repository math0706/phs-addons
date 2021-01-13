# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class StockPickingBatchRule(models.Model):
    _name = "stock.picking.batch.rule"
    _description = "Rules to create picking batch"

    name = fields.Char()

    filter_id = fields.Many2one(
        comodel_name="ir.filters",
        domain=[("model_id", "=", "stock.picking")],
        ondelete="restrict",
        required=True,
    )
    nbr_box = fields.Integer(default=9, required=True)
    nbr_order = fields.Integer(default=6, required=True)
    picking_type_id = fields.Many2one(comodel_name="stock.picking.type")
    sequence = fields.Integer(default=5)

    def batch_creation(self):
        ir_config = self.env["ir.config_parameter"]
        created_batch = self.env["stock.picking.batch"]
        pickings = self.env["stock.picking"]
        for batch_rule in self:
            pre_filtered_domain = [
                ("picking_type_id", "=", batch_rule.picking_type_id.id),
                ("state", "=", "assigned"),
            ]
            pickings = pickings.search(
                pre_filtered_domain + safe_eval(batch_rule.filter_id.domain)
            )
            nbr_order_in_a_batch = batch_rule.nbr_box * batch_rule.nbr_order
            for i in range(
                0,
                int(len(pickings) / nbr_order_in_a_batch) * nbr_order_in_a_batch,
                nbr_order_in_a_batch,
            ):
                new_batch = self.env["stock.picking.batch"].create(
                    {
                        "company_id": self.env.user.company_id.id,
                        "batch_rule_id": batch_rule.id,
                    }
                )
                pickings[i : i + nbr_order_in_a_batch].write({"batch_id": new_batch.id})
                created_batch += new_batch

        return created_batch

    def action_batch_creation(self):
        batch = self.batch_creation()

        return {
            "name": _("Picking Batch"),
            "view_mode": "tree,form",
            "res_model": "stock.picking.batch",
            "view_id": False,
            "type": "ir.actions.act_window",
            "domain": [("id", "in", batch.ids)],
        }


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    batch_rule_id = fields.Many2one(comodel_name="stock.picking.batch.rule")


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    batch_rule_ids = fields.One2many(
        comodel_name="stock.picking.batch.rule", inverse_name="picking_type_id"
    )


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def write(self, values):

        if not self.env.context.get("box_propagation", False) and len(self) == 1:
            batch_rule = self.move_id.picking_id.batch_id.batch_rule_id
            if len(batch_rule) == 1:
                nbr_order = batch_rule.nbr_order
            else:
                nbr_order = (
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("picking_box_nbr_order", 6)
                )
            if (
                "location_dest_id" in values
                and len(self) == 1
                and self.location_dest_id.name
                == self.env["ir.config_parameter"]
                .sudo()
                .get_param("dest_location_to_split_in_box", "Packing Zone")
            ):
                # Check that the destination box is not already used in an other open picking batch
                if len(
                    self.env["stock.move.line"].search(
                        [
                            ("location_dest_id", "=", values["location_dest_id"]),
                            (
                                "move_id.picking_id.batch_id.state",
                                "in",
                                ["draft", "in_progress"],
                            ),
                        ], limit=1
                    )
                ):
                    raise UserError(_("Box is not empty"))

                batch = self.move_id.picking_id.batch_id
                move_lines = self.search(
                    [
                        ("move_id.picking_id.batch_id.id", "=", batch.id),
                        ("location_dest_id.name", "=", "Packing Zone"),
                    ]
                )
                order_name_list = list(set(move_lines.mapped("origin")))
                order_name_list.remove(self.origin)
                order_name_list = [self.origin] + order_name_list[: nbr_order - 1]
                move_lines = self.search(
                    [
                        ("move_id.picking_id.batch_id.id", "=", batch.id),
                        ("location_dest_id.name", "=", "Packing Zone"),
                        ("origin", "in", order_name_list),
                    ]
                )
                move_lines.with_context(box_propagation=True).write(
                    {"location_dest_id": values["location_dest_id"]}
                )
                _logger.info(
                    "Box propagation for batch:{} box:{} and orders:{}".format(
                        batch.name, values["location_dest_id"], order_name_list
                    )
                )

        return super().write(values)
