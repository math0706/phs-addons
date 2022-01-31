# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import fields, models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = "stock.picking"

    date_quay = fields.Date(tracking=True)

    def put_at_dock(self):
        self.date_quay = date.today()
