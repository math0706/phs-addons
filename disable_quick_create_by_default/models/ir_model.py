from odoo import api, fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    avoid_quick_create = fields.Boolean(default=True)

    @api.model
    def disable_all_quick_create(self):
        self.search([]).write({"avoid_quick_create": True})
