# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

import logging
from datetime import date, timedelta
import base64
import requests
import shutil
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _gls_fr_glsbox_get_service(self, account, package=None):
        vals = self._roulier_get_service(account, package=package)

        vals["agencyId"] = "BE7100"
        vals["customerId"] = "0560004689"
        vals["parcel_total_number"] = 123
        
        return vals