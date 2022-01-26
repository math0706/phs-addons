# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, api, models

_logger = logging.getLogger(__name__)



class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    def _gls_fr_glsbox_get_parcel(self, picking):
        vals = self._roulier_get_parcel(picking)
        
        vals["custom_sequence"] = "1234567890"
        vals["parcel_number_barcode"] = 123
        vals["parcel_number_label"] = 123

        return vals