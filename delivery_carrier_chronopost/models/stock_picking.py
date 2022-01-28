# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime

import pytz

from odoo import fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"
    """ Product Code
        44 que pour la Belgique en livraison à domicile
        86 que pour la France point relais
        2L pour la france domicile
        Créer l'url de tracking"""

    def _chronopost_fr_get_service(self, account, package=None):
        vals = self._roulier_get_service(account, package=package)

        vals["customerId"] = str(self.partner_id.id)
        vals["labelFormat"] = "Z2D"
        vals["service"] = "0"
        user_tz = self.env.user.tz
        local = pytz.timezone(user_tz)
        hour = datetime.strftime(
            pytz.utc.localize(
                datetime.strptime(
                    str(fields.Datetime.now(local)), DEFAULT_SERVER_DATETIME_FORMAT
                )
            ).astimezone(local),
            "%H",
        )
        vals["shippingHour"] = int(hour)
        vals["shippingId"] = str(self.sale_id.id)
        if self.partner_id.delivery_point_ref:
            product = "86"
        else:
            if self.partner_id.country_id.code == "FR":
                product = "2L"
            else:
                product = "44"
        vals["product"] = product

        return vals

    def _chronopost_fr_get_from_address(self, package=None):
        vals = self._roulier_get_from_address(package=package)

        vals["civility"] = "M"

        return vals

    def _chronopost_fr_get_to_address(self, package=None):
        vals = self._roulier_get_to_address(package=package)

        vals["contact_name"] = self.partner_id.name
        vals["city"] = self.partner_id.city
        vals["country"] = self.partner_id.country_id.code
        vals["country_name"] = self.partner_id.country_id.name
        vals["name"] = self.partner_id.name
        vals["street1"] = self.partner_id.street
        vals["zip"] = self.partner_id.zip
        vals["email"] = self.partner_id.email
        vals["phone"] = self.partner_id.phone

        return vals
