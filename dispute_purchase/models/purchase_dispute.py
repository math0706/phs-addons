from odoo import _, api, models


class Dispute(models.Model):
    _inherit = ["dispute"]

    def _selection_model(self):
        selection_model = super()._selection_model()
        model_name = "purchase.order"
        selection_model.append((model_name, _(self.env[model_name]._description)))

        return selection_model

    @api.depends("model_ref_id")
    def _compute_partner_id(self):
        for r in self.filtered(
            lambda r: r.model_ref_id and r.model_ref_id._name == "purchase.order"
        ):
            r.partner_id = r.model_ref_id and r.model_ref_id.partner_id or False
        super()._compute_partner_id()

    def get_line_model_info(self, model_name):
        line_model_info = {
            "model_name": "purchase.order.line",
            "domain": "[('order_id.id', '=', dispute_model_ref_id.id)]",
            "product_id_field_name": "product_id",
        }
        if model_name == "purchase.order":
            # Force selection to only compatible sub_model of model_name
            return [line_model_info]
        else:
            super_info = super().get_line_model_info(model_name)
            if not model_name:
                super_info.append(line_model_info)
            return super_info

    def get_related_models(self):
        models = super().get_related_models()

        models += ["purchase.order"]

        return models


class DisputeLine(models.Model):
    _inherit = ["dispute.line"]

    def _compute_price_unit(self):
        if self.model_ref_id and self.model_ref_id._name == "purchase.order.line":
            for r in self:
                r.price_unit = r.model_ref_id.price_unit
        else:
            super()._compute_price_unit()

    def _on_change_model_ref_id(self):
        domains = {
            "purchase.order.line": [
                ("order_id.id", "=", self.dispute_id.model_ref_id.id)
            ],
            "product.product": [],
        }
        if self.model_ref_id and self.model_ref_id._name in domains:
            return {"domain": {"model_ref_id": domains[self.model_ref_id._name]}}
        else:
            return super()._on_change_model_ref_id()
