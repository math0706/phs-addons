import json

import requests
from dictor import dictor

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

FIELDS = {
    "odoo_field": [
        "name",
        "list_price",
        "taxes_id",
        "weight",
        "default_code",
        "barcode_ids",
    ],
    "API_field": ["name.fr", "publicPrice", "vat", "weight", "cnk", "ean"],
}


class ImportProduct(models.TransientModel):
    _name = "import.product.wizard"
    # ajouter une page sur le product avec le résultat de l'API
    result = fields.Char(readonly=True)
    import_field_ids = fields.One2many("import.product.field", "fields_id")
    code_type = fields.Selection(
        selection=[
            ("ean", "EAN"),
            ("cnk", "CNK"),
        ],
        string="Type",
        default="",
    )
    cnk = fields.Char(string="CNK")
    ean = fields.Char(string="EAN")
    product_id = fields.Many2one("product.template")
    name_fr = fields.Char()
    public_price = fields.Float()
    vat = fields.Many2one("account.tax")
    weight = fields.Float()

    @api.model
    def default_get(self, fields):
        product_id = self.env["product.template"].browse(
            self.env.context.get("active_ids")
        )
        res = super(ImportProduct, self).default_get(fields)

        res["product_id"] = product_id
        if product_id:
            if not self.import_field_ids:
                result = []
                list_barcodes = product_id.barcode_ids.mapped("name")
                list_barcodes.remove(product_id.default_code)
                list_code_type = ["cnk", "ean"]
                for code in list_barcodes:
                    for code_type in list_code_type:
                        if not result:
                            result = self.import_with_code(code, code_type)
                if result:
                    taxes = []
                    for taxe in product_id.taxes_id:
                        taxes.append(taxe.name)
                    res["import_field_ids"] = [
                        (
                            0,
                            0,
                            {
                                "list_fields": odoo_field,
                                "old_value": product_id.copy_data()[0].get(odoo_field)
                                if odoo_field
                                not in ["default_code", "barcode_ids", "taxes_id"]
                                else list_barcodes
                                if odoo_field == "barcode_ids"
                                else taxes
                                if odoo_field == "taxes_id"
                                else product_id.default_code,
                                "new_value": dictor(result, "results.0.%s" % API_field),
                            },
                        )
                        for odoo_field, API_field in zip(
                            FIELDS.get("odoo_field"), FIELDS.get("API_field")
                        )
                    ]
                else:
                    self.write({"result": "Pas de produits trouvé avec ces codes"})

        return res

    def import_new_product(self):
        if not self.product_id:
            code_type = self.code_type
            code = self.ean if self.code_type == "ean" else self.cnk
            medipim_product = self.import_with_code(code, code_type)

            vat = self.env["account.tax"].search([("name", "=", "21%")])
            if medipim_product:
                self.write(
                    {
                        "name_fr": dictor(medipim_product, "results.0.name.fr"),
                        "ean": dictor(medipim_product, "results.0.ean"),
                        "cnk": dictor(medipim_product, "results.0.cnk"),
                        "public_price": dictor(
                            medipim_product, "results.0.publicPrice", default=0
                        )
                        / 100,
                        "vat": vat.id,
                        "weight": dictor(medipim_product, "results.0.weight", default=0)
                        / 1000,
                    }
                )

            else:
                self.write({"result": "Pas de produits trouvé avec ces codes"})
            return {
                "name": "Import Product",
                "view_mode": "form",
                "view_id": False,
                "res_model": self._name,
                "domain": [],
                "context": dict(
                    self._context, active_ids=self.env.context.get("active_ids")
                ),
                "type": "ir.actions.act_window",
                "target": "new",
                "res_id": self.id,
            }

    def import_with_code(self, code, code_type):
        medipim_product = False
        response = self.import_from_api(code, code_type)
        result = json.loads(response.text)
        if result and result.get("results", False):
            medipim_product = result

        return medipim_product

    def import_product(self):
        if not self.env.context.get("active_ids"):
            product_id = self.env["product.template"].create(
                {
                    "name": self.name_fr,
                    "default_code": self.cnk,
                    "type": "product",
                    "categ_id": 1,
                    "lst_price": self.public_price,
                    "taxes_id": self.vat,
                    "weight": self.weight,
                }
            )

            for ean in safe_eval(self.ean):
                product_id.write(
                    {
                        "barcode_ids": [
                            (0, 0, {"name": ean, "product_id": product_id.id})
                        ]
                    }
                )

            return {
                "name": "form_name",
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "product.template",
                "res_id": product_id.id,
            }
        else:
            if len(self.env.context.get("active_ids")) == 1:
                product_id = self.env["product.template"].browse(
                    self.env.context.get("active_ids")
                )
                updated_field = {}
                for field in self.import_field_ids:
                    if field.update_field:
                        if field.list_fields == "taxes_id":
                            taxe_id = self.env["account.tax"].search(
                                [("name", "=", field.new_value + "%")]
                            )
                            if not taxe_id:
                                raise UserError(
                                    _("This taxe doesn't exist in the system")
                                )
                            else:
                                updated_field[field.list_fields] = taxe_id
                        elif field.list_fields == "list_price":
                            updated_field[field.list_fields] = (
                                int(field.new_value) / 100
                            )
                        elif field.list_fields == "weight":
                            updated_field[field.list_fields] = (
                                int(field.new_value) / 1000
                            )
                        elif field.list_fields == "barcode_ids":
                            barcode_ids = safe_eval(field.new_value)
                            for barcode in barcode_ids:
                                if barcode not in safe_eval(field.old_value):
                                    updated_field[field.list_fields] = [
                                        (
                                            0,
                                            0,
                                            {
                                                "name": barcode,
                                                "product_id": product_id.id,
                                            },
                                        )
                                    ]
                product_id.write(updated_field)

    def import_from_api(self, code, code_type):
        url = "https://api.medipim.be/v3/products/search"

        payload = (
            json.dumps(
                {
                    "filter": {"and": [{"status": "active"}, {"%s": code}]},
                }
            )
            % code_type
        )

        config_medipim = (
            self.env["ir.config_parameter"].sudo().get_param("config_medipim")
        )
        headers = {
            "14": safe_eval(config_medipim)["14"],
            "Authorization": safe_eval(config_medipim)["Authorization"],
            "Content-Type": "application/json",
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response)
        return response

    def update_all(self):
        for field in self.import_field_ids:
            field.update_field = True
        return {
            "name": "Import Product",
            "view_mode": "form",
            "view_id": False,
            "res_model": self._name,
            "domain": [],
            "context": dict(
                self._context, active_ids=self.env.context.get("active_ids")
            ),
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": self.id,
        }

    def update_none(self):
        for field in self.import_field_ids:
            field.update_field = False

        return {
            "name": "Import Product",
            "view_mode": "form",
            "view_id": False,
            "res_model": self._name,
            "domain": [],
            "context": dict(
                self._context, active_ids=self.env.context.get("active_ids")
            ),
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": self.id,
        }


class ImportProductField(models.TransientModel):
    _name = "import.product.field"

    fields_id = fields.Many2one("import.product.wizard")
    list_fields = fields.Char()
    old_value = fields.Char()
    new_value = fields.Char()
    update_field = fields.Boolean()
