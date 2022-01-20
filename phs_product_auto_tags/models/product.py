from datetime import datetime, timedelta

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def create(self, vals):
        tag_new_id = self.env.ref("phs_product_auto_tags.tag_new")
        if "tag_ids" in vals and tag_new_id.id not in vals["tag_ids"]:
            vals["tag_ids"].append((4, tag_new_id.id))

        return super(ProductTemplate, self).create(vals)

    def update_tag_new(self):
        nbr_days_tag_new = (
            self.env["ir.config_parameter"].sudo().get_param("nbr_days_tag_new", 10)
        )
        date_new_product = datetime.today() - timedelta(days=int(nbr_days_tag_new))
        new_tag_id = self.env.ref("phs_product_auto_tags.tag_new")
        self.search(
            [("tag_ids", "=", new_tag_id.id), ("create_date", "<", date_new_product)]
        ).write({"tag_ids": [(3, new_tag_id.id)]})

    def top_100_delivered_product(self):
        nbr_days_tag_top100 = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("nbr_days_tag_top100_delivered", 10)
        )
        date_nbr_days = datetime.today() - timedelta(days=int(nbr_days_tag_top100))
        tag_top_100_delivered = self.env.ref(
            "phs_product_auto_tags.tag_top_100_delivered"
        )
        product_list = self.env["sale.order.line"].read_group(
            [("create_date", ">", date_nbr_days)],
            fields=["qty_delivered"],
            groupby=["product_id", "qty_delivered"],
            limit=100,
            orderby="qty_delivered desc",
        )
        new_top_100_ids = [r for r in map(lambda r: r["product_id"][0], product_list)]
        new_top_100_ids = (
            self.env["product.product"]
            .search(["id", "in", new_top_100_ids])
            .mapped("product_tmpl_id")
        )
        self.search([("tag_ids", "=", tag_top_100_delivered.id)]).write(
            {"tag_ids": [(3, tag_top_100_delivered.id)]}
        )
        self.search(
            [
                ("id", "in", new_top_100_ids),
            ]
        ).write({"tag_ids": [(4, tag_top_100_delivered.id)]})
