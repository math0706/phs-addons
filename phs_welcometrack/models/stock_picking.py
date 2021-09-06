import logging
import re
from urllib.parse import urljoin

import requests
from requests.exceptions import HTTPError

from odoo import fields, models

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    label_checked = fields.Boolean(default=False, readonly=True, index=True)
    label_error = fields.Boolean(readonly=True, index=True)
    label_error_message = fields.Text(readonly=True)

    def action_debug_delivery_label(self):
        """Start Wizard to debug error in label generation .

        wizard that show a delivery address form,
        user can try to correct it until the label could be generated
        a log with the correction is created for further analysis.
        """
        action = self.env["ir.actions.actions"]._for_xml_id(
            "phs_welcometrack.debug_delivery_label_action"
        )
        action["context"] = {"default_picking_id": self.id}

        return action

    def _validate_wt_payload(self, payload):
        errors = []
        wt_payload_validation_rules = self._get_wt_payload_validation_rules()
        for k in payload:
            if k in wt_payload_validation_rules:
                rule = wt_payload_validation_rules[k]
                if re.match(rule, payload[k]) is None:
                    errors.append((k, payload[k]))
        return errors

    def _generate_payload_dest_address(self, address=None):
        """if address is set it could be any object
        with standard fields of res.partner address
        if not set the partner_id of the picking is used

        This is used in the debug label wizard to force an address
        without replacing it in the picking"""

        if address is None:
            address = self.partner_id
        address_payload = {
            "Address_City": address.city,
            "Address_Line1": address.street,
            "Address_Line2": address.street2 or "",
            "Address_ZipCode": address.zip,
            "Country_Code": address.country_id.code,
            "Recipient_Code": address.id,
            "Recipient_Email": address.email or "",
            "Recipient_FirstName": address.name,
            "Recipient_LastName": "",
            "Recipient_Mobile": address.mobile or "",
        }

        return address_payload

    def _generate_payload_order(self):

        order_payload = {
            "Order_Amount": self.sale_id.amount_total,
            "Order_Channel": self.sale_id.sale_channel_id
            and self.sale_id.sale_channel_id.name
            or "",
            "Order_DeliveryFees": 0,
            "Order_Reference": self.sale_id.name,
            "Order_Store": "????",
        }

        return order_payload

    def _generate_payload_label_info(self, check=False):
        label_info_payload = {
            "Label_Format": "PDF",
            "labelcheck": check and "1" or "0",
            "labeloutput": "binary",
        }

        return label_info_payload

    def _generate_payload_sender(self, carrier=None):
        if carrier is not None:
            sender_carrier = carrier
        else:
            sender_carrier = self.carrier_id

        sender_payload = {
            "Sender_City": sender_carrier.sender_id.city,
            "Sender_Line1": sender_carrier.sender_id.street,
            "Sender_Line2": sender_carrier.sender_id.street2 or "",
            "Sender_ZipCode": sender_carrier.sender_id.zip,
            "Sender_Company": "Pharmasimple",
            "Sender_CountryCode": sender_carrier.sender_id.country_id.code,
            "Warehouse_Code": "Defaut",
            "PhoneNumber": "",
        }

        return sender_payload

    def _generate_payload_carrier_login(self, carrier=None):
        if carrier is not None:
            sender_carrier = carrier
        else:
            sender_carrier = self.carrier_id
        wt_providerservice_code = (
            sender_carrier.carrier_account_id.wt_providerservice_code
        )
        carrier_login = {
            "carrierid": sender_carrier.carrier_account_id.wt_carrierid,
            "ProviderService_Code": wt_providerservice_code,
            "carrier_login": sender_carrier.carrier_account_id.account,
            "carrier_password": sender_carrier.carrier_account_id.password,
            "CustomerProvider_Account": sender_carrier.carrier_account_id.account,
        }

        return carrier_login

    def _generate_payload_package(self):

        package = {
            "Package_Weight": "1",
            "weightunit": "1",
        }

        return package

    def _generate_full_payload(self, check=False, address=None, carrier=None):
        wt_payload = {
            **self._generate_payload_carrier_login(carrier),
            **self._generate_payload_sender(),
            **self._generate_payload_label_info(check),
            **self._generate_payload_package(),
            **self._generate_payload_dest_address(address),
            **self._generate_payload_order(),
        }
        return wt_payload

    def _generate_shipping_labels(self, check=False, address=None, carrier=None):
        labels = []
        wt_payload = self._generate_full_payload(check, address, carrier)
        url = urljoin(self.carrier_id.carrier_account_id.api_url, "v5.0/Labels/INSERT")
        xapikey = self.carrier_id.carrier_account_id.api_key
        _logger.info("wt_payload {}", (wt_payload))
        error_message = None
        try:
            response = requests.get(url, json=wt_payload, headers={"xapikey": xapikey})
            response.raise_for_status()
        except HTTPError as http_err:
            _logger.debug(f"HTTP error occurred: {http_err}")
            error_message = http_err
        except Exception as err:
            _logger.debug(f"Other error occurred: {err}")
            error_message = err
        else:
            _logger.debug(response.text)
            response_json = response.json()
            if "ErrorCode" in response_json:
                error_message = response_json["ErrorMsg"]
            if not check:
                for key, value in response_json["DOCUMENTS"].items():
                    labels.append(
                        {
                            "name": "{}-{}".format(
                                response_json["DELIVERY_REFERENCE"], key
                            ),
                            "file": value["CONTENT"],
                            "file_type": value["FORMAT"],
                            "tracking_number": response_json["DELIVERY_REFERENCE"],
                        }
                    )
        return {"labels": labels, "error_message": error_message, "payload": wt_payload}

    def check_shipping_labels(self, address=None, carrier=None):
        _logger.debug("Check shipping_labels for picking {}", (self.name))
        label_error = False
        if self.carrier_id.is_welcometrack:
            labels = self._generate_shipping_labels(True, address, carrier)
            if labels["error_message"] is not None:
                self.env["shipping.label.error.log"].create(
                    {
                        "picking_id": self.id,
                        "log_type": "error",
                        "message": labels["error_message"],
                    }
                )
                label_error = True
                self.label_error_message = labels["error_message"]
        self.label_checked = True
        self.label_error = label_error
        return not label_error

    def action_check_shipping_labels(self):
        for picking in self:
            picking.check_shipping_labels()

    def send_to_shipper(self, check=False, address=None, carrier=None):
        _logger.debug("Generate shipping_labels for picking {}", (self.name))
        if self.carrier_id.is_welcometrack:
            res = self.carrier_id.welcometrack_send_shipping(self)
            labels = self._generate_shipping_labels(check, address, carrier)
            if labels["error_message"]:
                self.label_checked = True
                self.label_error = True
                self.label_error_message = labels["error_message"]
            result = []
            for res, label in zip(res, labels["labels"]):
                res["labels"] = [label]
                result.append(res)
            for result_dict, picking in zip(result, self):
                for label in result_dict.get("labels", []):
                    picking.attach_shipping_label(label)
            return result
        else:
            return super().generate_shipping_labels()
