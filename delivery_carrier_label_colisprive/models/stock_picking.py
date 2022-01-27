import base64
import re
from operator import attrgetter
from xml.etree import ElementTree

import requests

from odoo import _, exceptions, models

_compile_itemid = re.compile(r"[^0-9A-Za-z+\-_]")


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _colisprive_set_a_default_package(self):
        """Pickings using this module must have a package
        If not this method put it one silently
        """
        for picking in self:
            move_lines = picking.move_line_ids.filtered(
                lambda s: not (s.package_id or s.result_package_id)
            )
            if move_lines:
                carrier = picking.carrier_id
                default_packaging = carrier.colisprive_default_packaging_id
                package = self.env["stock.quant.package"].create(
                    {
                        "packaging_id": default_packaging
                        and default_packaging.id
                        or False
                    }
                )
                move_lines.write({"result_package_id": package.id})

    def _colisprive_get_packages_from_picking(self):
        """ Get all the packages from the picking """
        self.ensure_one()
        operation_obj = self.env["stock.move.line"]
        operations = operation_obj.search(
            [
                "|",
                ("package_id", "!=", False),
                ("result_package_id", "!=", False),
                ("picking_id", "=", self.id),
            ]
        )
        package_ids = set()
        for operation in operations:
            # Take the destination package. If empty, the package is
            # moved so take the source one.
            package_ids.add(operation.result_package_id.id or operation.package_id.id)

        packages = self.env["stock.quant.package"].browse(package_ids)
        return packages

    def colisprive_info_from_label(self, label):
        data = base64.b64encode(label["binary"])

        return {
            "labels": [
                {
                    "file": data,
                    "file_type": label["file_type"],
                    "name": "{}.{}".format(
                        label["tracking_number"], label["file_type"]
                    ),
                }
            ],
            "exact_price": False,
            "tracking_number": label["tracking_number"],
        }

    def write_tracking_number_label(self, label_result, packages):
        """
        If there are no pack defined, write tracking_number on picking
        otherwise, write it on parcel_tracking field of each pack.
        Note we can receive multiple labels for a same package
        """

        labels = []

        # It could happen that no successful label has been returned by the API
        if not label_result:
            return labels

        if not packages:
            label = label_result[0]["value"][0]
            self.carrier_tracking_ref = label["tracking_number"]
            labels.append(self.colisprive_info_from_label(label))

        tracking_refs = []
        for package in packages:
            tracking_numbers = []
            for label in label_result:
                for label_value in label["value"]:
                    if package.name in label_value["item_id"].split("+")[-1]:
                        tracking_numbers.append(label_value["tracking_number"])
                        labels.append(self.colisprive_info_from_label(label_value))
            package.parcel_tracking = "; ".join(tracking_numbers)
            tracking_refs += tracking_numbers

        existing_tracking_ref = (
            self.carrier_tracking_ref and self.carrier_tracking_ref.split("; ") or []
        )
        self.carrier_tracking_ref = "; ".join(existing_tracking_ref + tracking_refs)
        return labels

    def _get_itemid(self, picking, pack_no):
        """Allowed characters are alphanumeric plus `+`, `-` and `_`
        Last `+` separates picking name and package number (if any)

        :return string: itemid

        """
        name = _compile_itemid.sub("", picking.name)
        if not pack_no:
            return name

        pack_no = _compile_itemid.sub("", pack_no)
        codes = [name, pack_no]
        return "+".join(c for c in codes if c)

    def generate_colisprive_label(self, picking, packages):
        results = []

        url = "https://colisprive.com/Externe/WSCP.asmx"
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://colisprive.com/externe/1.0/SetParcel",
        }

        carrier_account = self.env["carrier.account"].search(
            [("carrier_ids", "=", picking.carrier_id.id)], limit=1
        )
        if not carrier_account:
            error_message = _("No carrier account defined")
            raise exceptions.Error(error_message)

        payload_con_data = {
            "UserName": carrier_account.account,
            "Password": carrier_account.password,
            "CPCustoID": carrier_account.colisprive_cpcustoid,
            "AccountID": carrier_account.colisprive_accountid,
        }
        ship_payload = """<?xml version="1.0" encoding="UTF-8"?>
        <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
                            xmlns:ns1="http://colisprive.com/externe/1.0/"
                            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <SOAP-ENV:Header>
                <ns1:AuthenticationHeader>
                    <ns1:UserName>{UserName}</ns1:UserName>
                    <ns1:Password>{Password}</ns1:Password>
                </ns1:AuthenticationHeader>
            </SOAP-ENV:Header>
            <SOAP-ENV:Body>
                <ns1:SetParcel>
                    <ns1:SetParcelRequest>
                        <ns1:SecurityID>
                            <ns1:CPCustoID>{CPCustoID}</ns1:CPCustoID>
                            <ns1:AccountID>{AccountID}</ns1:AccountID>
                        </ns1:SecurityID>
                        <ns1:OrderID>{OrderID}</ns1:OrderID>
                        <ns1:CltNum xsi:nil="true"/>
                        <ns1:CsgAdd>
                            <ns1:DlvrName>{DlvrName}</ns1:DlvrName>
                            <ns1:DlvrAddress>
                                <ns1:Add1>{Add1}</ns1:Add1>
                                <ns1:Add2>{Add2}</ns1:Add2>
                                <ns1:Add3>{Add3}</ns1:Add3>
                                <ns1:Add4>{Add4}</ns1:Add4>
                                <ns1:ZC>{ZC}</ns1:ZC>
                                <ns1:City>{City}</ns1:City>
                                <ns1:Country>{Country}</ns1:Country>
                            </ns1:DlvrAddress>
                            <ns1:DlvrEmail>{DlvrEmail}</ns1:DlvrEmail>
                            <ns1:DlvrPhon>{DlvrPhon}</ns1:DlvrPhon>
                            <ns1:DlvrGsm>{DlvrGsm}</ns1:DlvrGsm>
                        </ns1:CsgAdd>
                        <ns1:PclShipDate>2022 01 13</ns1:PclShipDate>
                        <ns1:PclWeight>5000</ns1:PclWeight>
                        <ns1:IsPclWithPOD>false</ns1:IsPclWithPOD>
                        <ns1:LabelFormat>PDF_ZEBRA</ns1:LabelFormat>
                        <ns1:ChargeAmnt xsi:nil="true"/>
                        <ns1:ValueAmnt xsi:nil="true"/>
                    </ns1:SetParcelRequest>
                </ns1:SetParcel>
            </SOAP-ENV:Body>
        </SOAP-ENV:Envelope>"""

        for package in packages:
            file_type = "pdf"
            order_payload = {
                "OrderID": "{}-{}".format(picking.origin, picking.name),
                "DlvrName": picking.partner_id.name,
                "Add1": picking.partner_id.street,
                "Add2": picking.partner_id.street2 or "",
                "Add3": "",
                "Add4": "",
                "ZC": picking.partner_id.zip,
                "City": picking.partner_id.city,
                "Country": picking.partner_id.country_id.code,
                "DlvrEmail": picking.partner_id.email or "",
                "DlvrPhon": picking.partner_id.phone or "",
                "DlvrGsm": picking.partner_id.mobile or "",
            }

            response = requests.request(
                "POST",
                url,
                headers=headers,
                data=ship_payload.format(**{**payload_con_data, **order_payload}),
            )
            dom = ElementTree.fromstring(response.content)

            pdf_response = requests.get(dom[0][0][0][3].text)

            binary = pdf_response.content

            res = {"value": []}
            res["success"] = True
            res["value"].append(
                {
                    "item_id": self._get_itemid(
                        picking, package.name if package else None
                    ),
                    "binary": binary,
                    "tracking_number": dom[0][0][0][1].text,
                    "file_type": file_type,
                }
            )
            results.append(res)
        return results

    def _generate_colisprive_label(self, package_ids=None):
        """ Generate labels """
        self.ensure_one()

        if package_ids is None:
            packages = self._colisprive_get_packages_from_picking()
            packages = packages.sorted(key=attrgetter("name"))
        else:
            # restrict on the provided packages
            package_obj = self.env["stock.quant.package"]
            packages = package_obj.browse(package_ids)

        # Do not generate label for packages that are already done
        packages = packages.filtered(lambda p: not p.parcel_tracking)

        label_results = self.generate_colisprive_label(self, packages)

        # Process the success packages first
        success_label_results = [
            label for label in label_results if "errors" not in label
        ]
        failed_label_results = [label for label in label_results if "errors" in label]

        # Case when there is a failed label, rollback odoo data
        if failed_label_results:
            self._cr.rollback()

        labels = self.write_tracking_number_label(success_label_results, packages)

        if failed_label_results:
            # Commit the change to save the changes,
            # This ensures the label pushed recored correctly in Odoo
            self._cr.commit()  # pylint: disable=invalid-commit
            error_message = "\n".join(label["errors"] for label in failed_label_results)
            raise exceptions.Warning(error_message)

        return labels

    def _generate_colisprive_shipping_label(self, package_ids=None):
        """ Add label generation for colisprive """
        self.ensure_one()
        res = self._generate_colisprive_label(package_ids=package_ids)

        return res
