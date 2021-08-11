from odoo import models, fields


class SaleRefundRequest(models.Model):
    _name = "sale.refund.request"

    name = fields.Char('name', readonly=True, default=lambda self: self.env["ir.sequence"].next_by_code("dispute"), copy=False)
    state = fields.Selection([
        ('draft', 'New'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')], 'State', default='draft')
    backorder_id = fields.Many2one('stock.picking', 'Link to Picking')
    so_id = fields.Many2one('sale.order', 'Link to Original SO')
    notes = fields.Text('Notes')
    product_ids = fields.One2many('sale.refund.product', 'request_id', 'Refunded products')
    total_amount = fields.Float('Total Refunded Amount', compute='_compute_total_amount',
                                readonly=True, store=True)
    invoice_id = fields.Many2one('account.invoice', 'Link to Customer Refund')
    partner_id = fields.Many2one('res.partner', 'SalesPerson')

class SaleRefundProduct(models.Model):
    _name = 'sale.refund.product'

    request_id = fields.Many2one('sale.refund.request', 'Request')
    product_id = fields.Many2one('product.product', 'Product')
    qty = fields.Float('Qty')
    unit_price = fields.Float('Price')