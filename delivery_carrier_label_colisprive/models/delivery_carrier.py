from odoo import fields, models


class DeliveryCarrier(models.Model):
    """ Add service group """

    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[("colisprive", "Colis privé")],
        ondelete={"colisprive": "set default"},
    )

    colisprive_default_packaging_id = fields.Many2one(
        "product.packaging", domain=[("package_carrier_type", "=", "colisprive")]
    )

    def colisprive_rate_shipment(self, order):
        self.ensure_one()
        delivery_product_price = self.product_id and self.product_id.lst_price or 0
        return {
            "success": True,
            "price": delivery_product_price,
            "error_message": False,
            "warning_message": False,
        }

    def colisprive_send_shipping(self, pickings):
        """
        It will generate the labels for all the packages of the picking.
        Packages are mandatory in this case
        """
        labels = []
        for pick in pickings:
            pick._colisprive_set_a_default_package()
            labels += pick._generate_colisprive_label()

        return labels
