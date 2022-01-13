from odoo import fields, models


class StockReceptionError(models.Model):
    _name = "stock.reception.error"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Stock Reception Error"

    name = fields.Char(
        copy=False,
        readonly=True,
        default=lambda self: self.env["ir.sequence"].next_by_code(
            "stock_reception_error"
        ),
    )
    state = fields.Selection(
        default="draft",
        selection=[
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
        ],
        tracking=True,
    )

    color = fields.Integer("Color Index", default=0)
    reception_date = fields.Date(required=True)
    description = fields.Html()
    line_ids = fields.One2many(
        comodel_name="stock.reception.error.line",
        inverse_name="stock_reception_error_id",
    )
    partner_id = fields.Many2one(comodel_name="res.partner", required=True)
    purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        required=True,
        domain="[('partner_id', '=',partner_id)]",
    )
    responsible_id = fields.Many2one(comodel_name="res.users")
    summary = fields.Text()


class StockReceptionErrorLine(models.Model):
    _name = "stock.reception.error.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Stock Reception Error line"

    def _compute_name(self):
        for r in self:
            r.name = r.product_id and r.product_id.name or r.product_description

    name = fields.Char(compute=_compute_name)
    stock_reception_error_id = fields.Many2one(comodel_name="stock.reception.error")
    comment = fields.Text()
    partner_id = fields.Many2one(
        related="stock_reception_error_id.partner_id", store=True
    )
    reception_date = fields.Date(
        related="stock_reception_error_id.reception_date", store=True
    )

    product_id = fields.Many2one(comodel_name="product.product")
    product_description = fields.Char()
    qty = fields.Float(required=True)
    reason = fields.Selection(
        [
            ("qty", "Quantity"),
            ("quality", "Quality"),
            ("other", "Others"),
        ],
        required=True,
    )
    resolution = fields.Selection(
        selection=[
            ("return", "Supplier return"),
            ("destruction", "Destruction"),
            ("ok_reception", "To receive"),
        ],
        tracking=True,
    )
    state = fields.Selection(
        default="draft",
        selection=[
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
        ],
        tracking=True,
    )
