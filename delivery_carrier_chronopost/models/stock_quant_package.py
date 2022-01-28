# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    def _chronopost_fr_get_parcel(self, picking):
        vals = self._roulier_get_parcel(picking)

        vals["objectType"] = "MAR"

        return vals
