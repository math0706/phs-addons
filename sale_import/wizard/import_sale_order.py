import base64
import csv
from io import StringIO

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError


class ImportSaleOrder(models.TransientModel):
    _name = "import.sale.order"

    partner_id = fields.Many2one("res.partner", string="Customer")
    file = fields.Binary("CSV File", required=True)
    filename = fields.Char()

    @api.constrains("filename", "file")
    def _check_filename(self):
        if self.file:
            if not self.filename:
                raise UserError(_("There is no file"))
            else:
                # Check the file's extension
                tmp = self.filename.split(".")
                ext = tmp[len(tmp) - 1]
                if ext != "csv":
                    raise UserError(_("The file must be a csv file"))

    def make(self):
        self.ensure_one()
        f = StringIO(base64.b64decode(self.file).decode("utf-8"))

        cpt = 0
        log = ""
        order_id = False
        for r in csv.reader(f, delimiter=";"):
            if not cpt:
                cpt += 1
                continue
            cnk = r[0]
            quantity = int(r[1])
            if not order_id:
                partner_id = self.partner_id
                order_id = self.env["sale.order"].create(
                    {
                        "partner_id": partner_id.id,
                    }
                )
            product_ids = self.env["product.product"].search(
                [("default_code", "=", cnk)], limit=1
            )
            if product_ids:
                product_id = product_ids[0]
                order_line_id = self.env["sale.order.line"].create(
                    {
                        "order_id": order_id.id,
                        "product_id": product_id.id,
                    }
                )
                # order_line_id.product_id_change()
                order_line_id.product_uom_qty = quantity
            else:
                log += f"Article manquant CNK:{cnk} Quantity :{quantity}\r\n"
            cpt += 1
        # if order_id and log:
        #     order_id.imported_log = log

        if order_id:
            action = self.env.ref("sale.action_quotations").read()[0]
            action["views"] = [(self.env.ref("sale.view_order_form").id, "form")]
            action["res_id"] = order_id.id
        else:
            action = {"type": "ir.actions.act_window_close"}

        return action
