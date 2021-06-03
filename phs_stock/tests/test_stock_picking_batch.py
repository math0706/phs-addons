from odoo.tests.common import TransactionCase
from odoo.tools.safe_eval import safe_eval


class TestStockPickingBatchRule(TransactionCase):
    """Tests for stock picking batch creation based on rules"""

    def setUp(self):
        super(TestStockPickingBatchRule, self).setUp()
        self.picking = self.env["stock.picking"]
        self.picking_batch = self.env["stock.picking.batch"]
        self.rules = self.env["stock.picking.batch.rule"]
        # clean existings rules
        self.rules.search([]).unlink()
        self.type_pick_out_id = self.env.ref("stock.picking_type_out")
        self.filter_all = self.env["ir.filters"].create(
            {
                "name": "All",
                "model_id": "stock.picking",
                "domain": "[]",
                "context": "{'group_by': []}",
                "sort": "[]",
            }
        )
        self.rule = self.rules.create(
            {
                "name": "All",
                "filter_id": self.filter_all.id,
                "nbr_box": 2,
                "nbr_order": 1,
                "picking_type_id": self.type_pick_out_id.id,
            }
        )

    def test_no_rule_no_batch(self):
        # No batch creation without rules
        force_create = False
        batch = self.rules.batch_creation(force_create)
        self.assertEqual(len(batch), 0)

    def test_rule_matching_all_pickings(self):
        """One rule matching all picking (8) split in batch of 2 orders
        expected result: 4 batch
        """
        force_create = False
        batch = self.rule.batch_creation(force_create)

        pre_filtered_domain = [
            ("picking_type_id", "=", self.rule.picking_type_id.id),
            ("state", "=", "assigned"),
            ("batch_id", "=", False),
        ]
        pickings = self.env["stock.picking"].search(
            pre_filtered_domain + safe_eval(self.rule.filter_id.domain)
        )
        self.assertEqual(len(batch), int(len(pickings) / 2))

    # def test_create_batch_picking_force_create(self):
    #     """The rule matching with 6 out of 8 split in 2 batch of 3 orders
    #     and the rest in an other batch
    #     expected result: 3 batch"""
    #     batch_1 = self.env.ref("stock_picking_batch.stock_picking_batch_1")
    #     batch_1.write({"state": "cancel"})
    #     batch_2 = self.env.ref("stock_picking_batch.stock_picking_batch_2")
    #     batch_2.write({"state": "cancel"})
    #     self.env.ref("stock_picking_batch.Picking_A").write({"batch_id": False})
    #     self.env.ref("stock_picking_batch.Picking_B").write({"batch_id": False})
    #     self.env.ref("stock_picking_batch.Picking_C").write({"batch_id": False})
    #     self.env.ref("stock_picking_batch.Picking_D").write({"batch_id": False})
    #     self.rule.write({"nbr_box": 3})
    #     force_create = True
    # batch = self.rule.batch_creation(force_create)

    # pre_filtered_domain = [
    #     ("picking_type_id", "=", self.rule.picking_type_id.id),
    #     ("state", "=", "assigned"),
    #     ("batch_id", "=", False),
    # ]
    # pickings = self.env["stock.picking"].search(
    #     pre_filtered_domain + safe_eval(self.rule.filter_id.domain)
    # )
    # self.assertEqual(len(batch), 3)
    # self.assertEqual(len(self.env["stock.picking.batch"].browse(batch[0]).picking_ids), 3)
    # self.assertEqual(len(self.env["stock.picking.batch"].browse(batch[1]).picking_ids), 3)
    # self.assertEqual(len(self.env["stock.picking.batch"].browse(batch[2]).picking_ids), 2)

    # def test_create_batch_picking_no_force_create(self):
    #     """The rule matching with 6 out of 8 split in 2 batch of 3 orders
    #     expected result: 2 batch"""
    #     self.rule.write({"nbr_box": 3})
    #     force_create = False
    # batch = self.rule.batch_creation(force_create)

    # pre_filtered_domain = [
    #     ("picking_type_id", "=", self.rule.picking_type_id.id),
    #     ("state", "=", "assigned"),
    #     ("batch_id", "=", False),
    # ]
    # pickings = self.env["stock.picking"].search(
    #     pre_filtered_domain + safe_eval(self.rule.filter_id.domain)
    # )
    # self.assertEqual(len(batch), 2)

    def test_cancel_batch(self):
        """when we cancel a batch, the field batch_id on picking must be set to False"""
        batch_ids = self.env["stock.picking.batch"].search([])
        move_lines = batch_ids[0].move_line_ids
        batch_ids[0].action_cancel()
        for move_line in move_lines:
            self.assertFalse(move_line.picking_id.batch_id)
