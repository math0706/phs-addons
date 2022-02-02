# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    def _compute_dispute_count(self):
        # # retrieve all children partners and prefetch 'parent_id' on them
        # all_partners = self.search([("id", "child_of", self.ids)])
        # all_partners.read(["parent_id"])

        for partner in self:
            partner.dispute_count = len(
                self.env["dispute"].search([("partner_id", "child_of", partner.id)])
            )

    dispute_count = fields.Integer(
        compute="_compute_dispute_count", string="Dispute Count"
    )

    def action_show_dispute_list(self):
        act_window = self.env.ref("dispute.dispute_action")
        act_window.domain = [("partner_id", "child_of", self.id)]

        return act_window.read()[0]
