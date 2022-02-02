# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import logging

import requests

from odoo import models

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _mondialrelay_get_service(self, account, package=None):
        vals = self._roulier_get_service(account, package=package)

        vals["pickupMode"] = "CCC"
        vals["shippingCountry"] = self.partner_id.country_id.code
        vals["shippingSite"] = self.partner_id.delivery_point_ref
        vals["shippingId"] = self.id
        vals["customerId"] = self.partner_id.id
        vals["product"] = "24R"

        return vals

    def _mondialrelay_get_from_address(self, package=None):
        vals = self._roulier_get_from_address(package=package)

        vals["lang"] = "FR"
        vals["phone"] = self.company_id.phone

        return vals

    def _mondialrelay_get_to_address(self, package=None):
        vals = self._roulier_get_to_address(package=package)

        vals["lang"] = "FR"

        return vals

    def _roulier_generate_labels(self):
        res = super(StockPicking, self)._roulier_generate_labels()
        if self.delivery_type == "mondialrelay":
            if res[0].get("labels")[0].get("file"):
                url = res[0].get("labels")[0].get("file")
                url = url.replace("format=A4", "format=10x15")
                response = requests.get(url)
                if response.status_code == 200:
                    label = res[0].get("labels")[0]
                    label["file"] = base64.b64encode(response.content)
                    label["name"] = "mondial_label.pdf"
                    label["file_type"] = "pdf"
                else:
                    print("Error: " + response.text)

        return res
