# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _gls_fr_glsbox_get_service(self, account, package=None):
        vals = self._roulier_get_service(account, package=package)

        vals["agencyId"] = "BE7100"
        vals["customerId"] = "0560004689"
        vals["parcel_total_number"] = 1

        return vals
