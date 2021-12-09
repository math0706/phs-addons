# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class StockPickingBatchRule(models.Model):
    _name = "stock.picking.batch.rule"
    _description = "Rules to create picking batch"

    @api.depends("filter_id", "nbr_box", "nbr_order")
    def _compute_nbr_batch(self):
        for record in self:
            if record.filter_id:
                pickings = self.env["stock.picking"].search(
                    safe_eval(record.filter_id.domain)
                )
                nbr_order_in_a_batch = record.nbr_box * record.nbr_order
                record.nbr_batch = int(len(pickings) / nbr_order_in_a_batch)

    name = fields.Char()

    filter_id = fields.Many2one(
        comodel_name="ir.filters",
        domain=[("model_id", "=", "stock.picking")],
        ondelete="restrict",
        required=True,
    )
    nbr_box = fields.Integer(default=9, required=True)
    nbr_order = fields.Integer(default=6, required=True)
    nbr_batch = fields.Integer(
        readonly=True,
        compute="_compute_nbr_batch",
        default=0,
        string="Number of complete batch",
    )
    picking_type_id = fields.Many2one(comodel_name="stock.picking.type")
    sequence = fields.Integer(default=5)

    def batch_creation(self, force_create, nbr_batch):
        created_batch = self.env["stock.picking.batch"]
        pickings = self.env["stock.picking"]
        for batch_rule in self:
            pickings = self.env["stock.picking"].search(
                safe_eval(self.filter_id.domain)
            )
            nbr_order_in_a_batch = batch_rule.nbr_box * batch_rule.nbr_order
            if nbr_batch <= int(len(pickings) / nbr_order_in_a_batch):
                nbr_batch_to_create = nbr_batch * nbr_order_in_a_batch
            else:
                nbr_batch_to_create = (
                    int(len(pickings) / nbr_order_in_a_batch) * nbr_order_in_a_batch
                )

            for i in range(
                0,
                nbr_batch_to_create,
                nbr_order_in_a_batch,
            ):
                new_batch = self.create_new_batch(batch_rule)
                pickings[i : i + nbr_order_in_a_batch].write({"batch_id": new_batch.id})
                created_batch += new_batch
            if force_create:
                rest_of_picking = pickings.filtered(
                    lambda r: r.id not in created_batch.picking_ids.ids
                )
                if len(rest_of_picking) < nbr_batch * nbr_order_in_a_batch:
                    if (
                        rest_of_picking
                        and int(len(rest_of_picking) / nbr_order_in_a_batch) < 1
                    ):
                        new_batch = self.create_new_batch(batch_rule)
                        for picking in rest_of_picking:
                            picking.write({"batch_id": new_batch.id})
                        created_batch += new_batch

        return created_batch.ids

    def create_new_batch(self, batch_rule):
        new_batch = self.env["stock.picking.batch"].create(
            {
                "company_id": self.env.user.company_id.id,
                "batch_rule_id": batch_rule.id,
            }
        )
        return new_batch


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    batch_rule_id = fields.Many2one(comodel_name="stock.picking.batch.rule")

    def action_cancel(self):
        res = super().action_cancel()
        for move_line in self.move_line_ids:
            move_line.picking_id.write({"batch_id": False})
        return res


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    batch_rule_ids = fields.One2many(
        comodel_name="stock.picking.batch.rule", inverse_name="picking_type_id"
    )


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _check_if_so_allready_in_box(self, location):
        """Check that the box allready contain a product of the same order"""
        if len(
            self.env["stock.move.line"].search(
                [
                    ("location_dest_id", "=", location),
                    (
                        "move_id.picking_id.batch_id.state",
                        "in",
                        ["draft", "in_progress"],
                    ),
                    ("origin", "=", self.origin),
                ],
                limit=1,
            )
        ):
            return True
        else:
            return False

    def _check_if_so_in_other_box(self, location):
        """Check that the box allready contain a product of the same order"""
        move_line = self.env["stock.move.line"].search(
            [
                (
                    "location_dest_id.id",
                    "!=",
                    self.move_id.picking_type_id.default_location_dest_id.id,
                ),
                ("location_dest_id", "!=", location),
                (
                    "move_id.picking_id.batch_id.state",
                    "in",
                    ["draft", "in_progress"],
                ),
                ("origin", "=", self.origin),
            ],
            limit=1,
        )
        if len(move_line):
            return move_line.location_dest_id
        else:
            return False

    def _get_nbr_so_in_box(self, location):
        lines = self.env["stock.move.line"].search(
            [
                ("location_dest_id", "=", location),
                (
                    "move_id.picking_id.batch_id.state",
                    "in",
                    ["draft", "in_progress"],
                ),
            ],
        )
        return len(list(set(lines.mapped("origin"))))

    def write(self, values):

        if (
            len(self) == 1
            and "location_dest_id" in values
            and not self._check_if_so_allready_in_box(values["location_dest_id"])
        ):
            last_scanned_box = self._check_if_so_in_other_box(
                values["location_dest_id"]
            )
            if last_scanned_box and last_scanned_box.id != values["location_dest_id"]:
                raise UserError(_(f"Scan the correct box - {last_scanned_box.name}"))

            batch_rule = self.move_id.picking_id.batch_id.batch_rule_id
            if len(batch_rule) == 1:
                nbr_order = batch_rule.nbr_order
            else:
                nbr_order = (
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("picking_box_nbr_order", 6)
                )
            if self._get_nbr_so_in_box(values["location_dest_id"]) >= nbr_order:
                raise UserError(_("Choose an other box"))

        return super().write(values)
