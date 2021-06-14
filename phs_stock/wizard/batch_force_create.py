from odoo import _, fields, models


class BatchForceCreate(models.TransientModel):
    _name = "batch.force.create"

    force_create = fields.Boolean(default=False)

    def confirm(self):
        picking_batch_rule_id = self.env["stock.picking.batch.rule"].browse(
            self.env.context.get("active_id")
        )
        created_batch = picking_batch_rule_id.batch_creation(self.force_create)

        return {
            "name": _("Picking Batch"),
            "view_mode": "tree,form",
            "res_model": "stock.picking.batch",
            "view_id": False,
            "type": "ir.actions.act_window",
            "domain": [("id", "in", created_batch)],
        }
