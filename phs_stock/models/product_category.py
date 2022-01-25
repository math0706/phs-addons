from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    no_order_box_limit = fields.Boolean(
        help="""This falg determine if during the picking process,
        products ca be put in the same box,
        no matter the number of order limit of the batch rule"""
    )
