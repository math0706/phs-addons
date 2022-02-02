# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    purchase_user_id = fields.Many2one(
        comodel_name="res.users", string="Purchase Responsible"
    )
