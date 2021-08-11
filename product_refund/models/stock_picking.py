from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    refund_request_id = fields.Many2one(string="Product Refund", comodel_name="sale.refund.request", readonly=True)

    def _check_backorder(self):
        # If strategy == 'manual', let the normal process going on
        self = self.filtered(lambda p: p.picking_type_id.backorder_strategy == "manual")
        return super(StockPicking, self)._check_backorder()

    def _create_backorder(self):
        # Do nothing with pickings 'no_create'
        pickings = self.filtered(
            lambda p: p.picking_type_id.backorder_strategy != "no_create"
        )
        pickings_no_create = self - pickings
        pickings_no_create.mapped("move_lines")._cancel_remaining_quantities()
        res = super(StockPicking, pickings)._create_backorder()
        to_cancel = res.filtered(
            lambda b: b.backorder_id.picking_type_id.backorder_strategy == "cancel"
        )
        to_cancel.action_cancel()
        if res.picking_type_id.name == "Pick":
            to_cancel.create_refund_request(res)

        return res
    
    def create_refund_request(self, res):
        refund_request_model = self.env["sale.refund.request"]
        vals = {
            'state': 'draft',
            'backorder_id': res.id,
            'so_id': res.sale_id.id,
            'partner_id': res.partner_id.id,
            }
        request_id = refund_request_model.create(vals)
        total_refund = 0
        for move_line in res.move_ids_without_package:
            self.env['sale.refund.product'].create(
                {
                    'request_id': request_id.id,
                    'product_id': move_line.product_id.id,
                    'qty': move_line.product_uom_qty,
                    'unit_price': move_line.product_id.lst_price,
                })
            total_refund += move_line.product_uom_qty*move_line.product_id.lst_price
        request_id.write({'total_amount': total_refund})
        res.write({'refund_request_id': request_id.id})

        account_move_reversal_id = self.env['account.move.reversal'].create(
            {
                'move_ids': [(6, 0, res.sale_id.invoice_ids.ids)],
                'date_mode': 'custom',
                'reason': 'all products could not be delivered',
                'refund_method': 'refund',
                'company_id': self.company_id.id,
                'currency_id': res.sale_id.invoice_ids.currency_id.id,
            })
        account_move_reversal_id.reverse_moves()
