# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import math

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    def _gls_fr_glsbox_get_parcel(self, picking):
        vals = self._roulier_get_parcel(picking)

        vals["custom_sequence"] = "7164289396"
        vals["parcel_number_barcode"] = 1
        vals["parcel_number_label"] = 1
        vals["parcel_sequence"] = self.calc_parcel_num()
        return vals

    @api.model
    def _get_sequence(self):
        sequence = self.env["ir.sequence"].next_by_code("delivery_carrier_gls")
        if not sequence:
            raise UserError(_("There is no sequence defined for the label GLS"))
        return sequence

    def calc_parcel_num(self):
        start_num = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("PARCEL_NUM_START", 71642892000)
        )
        parcel_num = self._get_sequence()
        num = int(start_num) + int(parcel_num)
        num = str(num)
        num = list(num)
        num.reverse()
        weighting = 3
        sum_of_num = 0
        for item in num:
            sum_of_num += int(item) * weighting
            if weighting == 3:
                weighting = 1
            else:
                weighting = 3
        sum_of_num += 1
        check_num = int(math.ceil(sum_of_num / 10.0)) * 10 - sum_of_num
        num.reverse()
        num.append(str(check_num))
        return "".join(num)
