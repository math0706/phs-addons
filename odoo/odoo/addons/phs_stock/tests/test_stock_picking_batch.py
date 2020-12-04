from odoo.tests.common import TransactionCase


class TestStockPickingBatchRule(TransactionCase):
    """Tests for stock picking batch creation based on rules"""

    def setUp(self):
        super(TestStockPickingBatchRule, self).setUp()
        self.so = self.env['sale.order']
        self.picking = self.env['stock.picking']
        self.picking_batch = self.env['stock.picking.batch']
        self.rules = self.env['stock.picking.batch.rule']
        # clean existings rules
        self.rules.search([]).unlink()
        # validate all existing pickings
        pickings_to_validate = self.env['stock.picking'].search([('state', '=', 'assigned')])
        pickings_to_validate.with_context(cancel_backorder=True)._action_done()
        # update stock qty to force availability for future pickings
        self.partner_id = self.env['res.partner'].create({'name': 'Wood Corner Partner'})
        self.product_id_1 = self.env['product.product'].create({'name': 'Large Desk'})
        self.product_id_2 = self.env['product.product'].create({'name': 'Conference Chair'})
        self.po_vals = {
            'partner_id': self.partner_id.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_id_1.name,
                    'product_id': self.product_id_1.id,
                    'product_qty': 5.0,
                    'product_uom': self.product_id_1.uom_po_id.id,
                    'price_unit': 500.0,
                })],
        }
        po = self.env['purchase.order'].create(self.po_vals)

        po.order_line.product_qty = 1000
        po.button_confirm()

        first_picking = po.picking_ids
        first_picking.move_lines.quantity_done = 1000
        first_picking.button_validate()
        # create orders
        for i in range(0,50):
            so = self.so.create({'partner_id': self.env.ref("base.res_partner_12").id,
                            'order_line': [(0, 0, {'product_id': self.product_id_1.id,
                                                'product_uom_qty': 1,
                                                'price_unit': 5})]})
            so.action_confirm()


    def test_no_rule_no_batch(self):
        # No batch creation without rules
        batch = self.rules.batch_creation()
        self.assertEqual(len(batch), 0)

    def test_rule_matching_all_pickings(self):
        """One rule matching all picking (50) split in batch of 3 orders
            expected result: 8 batch
        """
        filter_all = self.env['ir.filters'].create({'name': 'All',
                                                    'model_id': 'stock.picking',
                                                    'domain': '[]',
                                                    'context': "{'group_by': []}",
                                                    'sort': '[]'})
        rule = self.rules.create({'name': 'All',
                            'filter_id': filter_all.id,
                            'nbr_box': 2,
                            'nbr_order': 3,
                            'picking_type_id': self.env['stock.picking.type'].search([('name', '=', 'Pack')])[0].id,
                            })
        batch = rule.batch_creation()
        self.assertEqual(len(batch), 8)
    