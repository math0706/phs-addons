from odoo import fields, models


class DeliveryCarrier(models.Model):
    """ Add service group """

    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[("pharmasimple", "Pharmasimple")],
        ondelete={"pharmasimple": "set default"},
    )

    pharmasimple_default_packaging_id = fields.Many2one(
        "product.packaging", domain=[("package_carrier_type", "=", "pharmasimple")]
    )

    def pharmasimple_rate_shipment(self, order):
        self.ensure_one()
        delivery_product_price = self.product_id and self.product_id.lst_price or 0
        return {
            "success": True,
            "price": delivery_product_price,
            "error_message": False,
            "warning_message": False,
        }

    def pharmasimple_send_shipping(self, pickings):
        """
        It will generate the labels for all the packages of the picking.
        Packages are mandatory in this case
        """
        for pick in pickings:
            pick._set_a_default_package()
            pick._generate_pharmasimple_label()

        return [{"exact_price": False, "tracking_number": False}]
