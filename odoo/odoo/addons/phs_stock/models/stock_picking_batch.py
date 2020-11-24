# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


from odoo import api, fields, models


from odoo import api, fields, models


class StockPickingBatchRule(models.Model):
    _name = 'stock.picking.batch.rule'
    _description = 'Rules to create picking batch'

    name = fields.Char()
    sequence = fields.Integer(default=5)
    filter_id = fields.Many2one(comodel_name='ir.filters', domain=[('model_id', '=', 'stock.picking')], ondelete='restrict', required=True)
    nbr_box = fields.Integer(default=9, required=True)
    nbr_order = fields.Integer(default=6, required=True)

class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    # def batch_automatic_creation(self):
    #     # TODO: create an admin interface
    #     ir_config = self.env["ir.config_parameter"]
    #     operation_types = ir_config.sudo().get_param("batch_operation_type", ['Pick'])
    #     nbr_order = ir_config.sudo().get_param("nbr_order_batch", 6)
    #     created_batch = self.env['stock.picking.batch']
    #     pickings = self.env['stock.picking']
    #     for ot in operation_types:
    #         pickings = pickings.search([('batch_id', '=', False),
    #                                     ('state', '=', 'assigned'),
    #                                     ('picking_type_id.name', '=', ot)])
    #         # TODO: Check if picking match an invoiced order
    #         for i in range(0,int(len(pickings)/nbr_order)*nbr_order,nbr_order):
    #             new_batch = self.create({'company_id': self.env.user.company_id.id})
    #             pickings[i:i+nbr_order].write({'batch_id': new_batch.id})
    #             created_batch += new_batch
        
    #     return created_batch

    def batch_automatic_creation(self):
        ir_config = self.env["ir.config_parameter"]
        created_batch = self.env['stock.picking.batch']
        pickings = self.env['stock.picking']
        for batch_rule in self.env['stock.picking.batch.rule'].search([]):
            pickings = pickings.search(eval(batch_rule.filter_id.domain))
            # Remove not candidate pickings 
            pickings = pickings.filtered(lambda r: r.picking_type_id.name == 'Pick' and r.state == 'assigned' and len(r.batch_id) == 0)
            # TODO: Check if picking match an invoiced order
            nbr_order_in_a_batch = batch_rule.nbr_box * batch_rule.nbr_order
            for i in range(0,int(len(pickings)/nbr_order_in_a_batch)*nbr_order_in_a_batch,nbr_order_in_a_batch):
                new_batch = self.create({'company_id': self.env.user.company_id.id})
                pickings[i:i+nbr_order_in_a_batch].write({'batch_id': new_batch.id})
                created_batch += new_batch
        
        return created_batch

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def write(self, values):
        nbr_order = self.env["ir.config_parameter"].sudo().get_param("nbr_order_box", 2)

        if not self.env.context.get("box_propagation", False):
            if (
                "location_dest_id" in values
                and len(self) == 1
                and self.location_dest_id.name == "Packing Zone"
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
                        ]
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
