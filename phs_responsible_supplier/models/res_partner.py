from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    responsible_supplier_id = fields.Many2one(
        string="Responsible Supplier", comodel_name="res.partner"
    )
