# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    def _compute_dispute_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.search([("id", "child_of", self.ids)])
        all_partners.read(["parent_id"])

        for partner in self:
            partner.dispute_count = len(
                self.env["dispute"].search([("partner_id", "in", all_partners.ids)])
            )

    dispute_count = fields.Integer(
        compute="_compute_dispute_count", string="Dispute Count"
    )
