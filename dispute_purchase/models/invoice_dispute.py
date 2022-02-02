from odoo import _, api, models


class Dispute(models.Model):
    _inherit = ["dispute"]

    def _selection_model(self):
        selection_model = super()._selection_model()
        model_name = "account.move"
        selection_model.append((model_name, _(self.env[model_name]._description)))

        return selection_model

    @api.depends("model_ref_id")
    def _compute_partner_id(self):
        for r in self.filtered(
            lambda r: r.model_ref_id and r.model_ref_id._name == "account.move"
        ):
            r.partner_id = r.model_ref_id and r.model_ref_id.partner_id or False
        super()._compute_partner_id()

    def get_line_model_info(self, model_name):
        line_model_info = {
            "model_name": "account.move.line",
            "domain": "[('move_id.id', '=', dispute_model_ref_id.id)]",
            "product_id_field_name": "product_id",
        }
        if model_name == "account.move":
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
