# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    def _mondialrelay_get_parcel(self, picking):
        vals = self._roulier_get_parcel(picking)
        weight = 0
        for line in self.planned_move_line_ids:
            weight += line.product_id.weight
        if weight == 0:
            weight = 0.1
        vals["weight"] = weight

        return vals
