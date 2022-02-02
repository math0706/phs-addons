# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def create(self, vals):
        if (
            self.env["res.users"].browse(self.env.context["uid"]).id
            == self.env["res.partner"].browse(vals["partner_id"]).purchase_user_id.id
            or self.env["res.users"].browse(self.env.context["uid"]).name
            == "Administrator"
        ):
            vals["user_id"] = (
                self.env["res.partner"].browse(vals["partner_id"]).purchase_user_id.id
            )
        else:
            vals["user_id"] = self.env["res.users"].browse(self.env.context["uid"]).id
        return super(PurchaseOrder, self).create(vals)
