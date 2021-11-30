import base64
import re
from operator import attrgetter

from odoo import exceptions, models

_compile_itemid = re.compile(r"[^0-9A-Za-z+\-_]")


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def get_shipping_label_values(self, label):
        self.ensure_one()
        return {
            "name": label["name"],
            "res_id": self.id,
            "res_model": "stock.picking",
            "datas": label["file"],
            "file_type": label["file_type"],
        }

    def _set_a_default_package(self):
        """Pickings using this module must have a package
        If not this method put it one silently
        """
        for picking in self:
            move_lines = picking.move_line_ids.filtered(
                lambda s: not (s.package_id or s.result_package_id)
            )
            if move_lines:
                carrier = picking.carrier_id
                default_packaging = carrier.pharmasimple_default_packaging_id
                package = self.env["stock.quant.package"].create(
                    {
                        "packaging_id": default_packaging
                        and default_packaging.id
                        or False
                    }
                )
                move_lines.write({"result_package_id": package.id})

    def _get_packages_from_picking(self):
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

    def info_from_label(self, label):
        data = base64.b64decode(label["binary"])

        return {
            "file": data,
            "file_type": label["file_type"],
            "name": "1234" + "." + label["file_type"],
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
            labels.append(self.info_from_label(label))

        tracking_refs = []
        for package in packages:
            tracking_numbers = []
            for label in label_result:
                for label_value in label["value"]:
                    if package.name in label_value["item_id"].split("+")[-1]:
                        tracking_numbers.append(label_value["tracking_number"])
                        labels.append(self.info_from_label(label_value))
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

    def generate_label(self, picking, packages):
        results = []

        for package in packages:
            file_type = "pdf"
            pdf, pdf_format = (
                self.env.ref("phs_delivery_label.phs_delivery_label_report")
                .sudo()
                ._render_qweb_pdf(picking.ids)
            )
            # binary = base64.b64encode(bytes(pdf, "utf-8"))
            binary = pdf
            res = {"value": []}
            res["success"] = True
            res["value"].append(
                {
                    "item_id": self._get_itemid(
                        picking, package.name if package else None
                    ),
                    "binary": binary,
                    "tracking_number": "1234",
                    "file_type": file_type,
                }
            )
            results.append(res)
        return results

    def _generate_pharmasimple_label(self, package_ids=None):
        """ Generate labels """
        self.ensure_one()

        if package_ids is None:
            packages = self._get_packages_from_picking()
            packages = packages.sorted(key=attrgetter("name"))
        else:
            # restrict on the provided packages
            package_obj = self.env["stock.quant.package"]
            packages = package_obj.browse(package_ids)

        # Do not generate label for packages that are already done
        packages = packages.filtered(lambda p: not p.parcel_tracking)

        label_results = self.generate_label(self, packages)

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

    def generate_pharmasimple_shipping_labels(self, package_ids=None):
        """ Add label generation for Pharmasimple """
        self.ensure_one()
        return self._generate_pharmasimple_label(package_ids=package_ids)
