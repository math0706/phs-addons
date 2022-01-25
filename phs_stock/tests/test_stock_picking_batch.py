from odoo.exceptions import UserError
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
                "domain": """[('picking_type_id', '=', {}),
                            ('state', 'in', ['assigned'])]""".format(
                    self.type_pick_out_id.id
                ),
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
        self.output_loc = self.env.ref("stock.stock_location_output")
        self.bac1 = self.env["stock.location"].create(
            {"name": "BAC-0001", "location_id": self.output_loc.id}
        )
        self.bac2 = self.env["stock.location"].create(
            {"name": "BAC-0002", "location_id": self.output_loc.id}
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
        batch_1 = self.env.ref("stock_picking_batch.stock_picking_batch_1")
        batch_1.action_cancel()
        batch_2 = self.env.ref("stock_picking_batch.stock_picking_batch_2")
        batch_2.action_cancel()
        force_create = False
        batch = self.rule.batch_creation(force_create)

        pre_filtered_domain = [
            ("picking_type_id", "=", self.rule.picking_type_id.id),
            ("state", "=", "assigned"),
        ]
        pickings = self.env["stock.picking"].search(
            pre_filtered_domain + safe_eval(self.rule.filter_id.domain)
        )
        self.assertEqual(len(batch), int(len(pickings) / 2))

    def test_create_batch_picking_force_create(self):
        """The rule matching with 6 out of 8 split in 2 batch of 3 orders
        and the rest in an other batch
        expected result: 3 batch"""
        batch_1 = self.env.ref("stock_picking_batch.stock_picking_batch_1")
        batch_1.action_cancel()
        batch_2 = self.env.ref("stock_picking_batch.stock_picking_batch_2")
        batch_2.action_cancel()
        self.rule.write({"nbr_box": 3})
        force_create = True
        batch = self.rule.batch_creation(force_create)

        self.assertEqual(len(batch), 2)

    def test_create_batch_picking_no_force_create(self):
        """The rule matching with 6 out of 8 split in 2 batch of 3 orders
        expected result: 2 batch"""
        batch_1 = self.env.ref("stock_picking_batch.stock_picking_batch_1")
        batch_1.action_cancel()
        batch_2 = self.env.ref("stock_picking_batch.stock_picking_batch_2")
        batch_2.action_cancel()
        self.rule.write({"nbr_box": 3})
        force_create = False
        batch = self.rule.batch_creation(force_create)

        self.assertEqual(len(batch), 1)

    def test_cancel_batch(self):
        """when we cancel a batch, the field batch_id on picking must be set to False"""
        batch_ids = self.env["stock.picking.batch"].search([])
        move_lines = batch_ids[0].move_line_ids
        batch_ids[0].action_cancel()
        for move_line in move_lines:
            self.assertFalse(move_line.picking_id.batch_id)

    def test_category_no_limit(self):
        """Product from catagory with "no order limit in box" settings
        can be put all in the same box,
        no matter the box attributed to the others products from the same order
        and no matter the number of order already in the destination box"""

        self.picking_batch.search([]).mapped(lambda r: r.action_cancel())
        batch = self.rule.batch_creation(True)[0]
        batch[0].picking_ids.move_line_ids.mapped("product_id.categ_id").write(
            {"no_order_box_limit": True}
        )
        try:
            for line in batch[0].picking_ids.move_line_ids:
                line.write({"location_dest_id": self.bac1.id})
        except Exception as e:
            self.fail("test_category_no_limit raise unwanted error:{}".format(e))

    def test_category_with_limit(self):
        """Product from catagory with "no order limit in box" settings
        can be put all in the same box,
        no matter the box attributed to the others products from the same order
        and no matter the number of order already in the destination box"""

        self.picking_batch.search([]).mapped(lambda r: r.action_cancel())
        batch = self.rule.batch_creation(True)[0]
        batch[0].picking_ids.move_line_ids.mapped("product_id.categ_id").write(
            {"no_order_box_limit": False}
        )
        with self.assertRaises(UserError):
            for line in batch[0].picking_ids.move_line_ids:
                line.write({"location_dest_id": self.bac1.id})
