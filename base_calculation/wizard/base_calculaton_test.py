# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo import api, fields, models


class BaseCalculationTest(models.TransientModel):
    _name = "base.calculation.test"
    _description = "Base Calculation Test"

    @api.model
    def _selection_target_model(self):
        return [
            (model.model, model.name)
            for model in self.env["ir.model"].sudo().search([])
        ]

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        if not result.get("base_calculation_id") or "resource_ref" not in fields:
            return result
        base_calculation = (
            self.env["base.calculation"].browse(result["base_calculation_id"]).sudo()
        )
        model = base_calculation.model
        res = self.env[model].search([], limit=1)
        if res:
            result["resource_ref"] = f"{model},{res.id}"
        return result

    base_calculation_id = fields.Many2one(
        "base.calculation", string="Related Base Calculation", required=True
    )
    model_id = fields.Many2one(
        "ir.model", string="Targeted model", related="base_calculation_id.model_id"
    )
    reference = fields.Char(related="base_calculation_id.reference")
    resource_ref = fields.Reference(
        string="Record", selection="_selection_target_model"
    )
    error_msg = fields.Char("Error Message", readonly=True)
    calculation_result = fields.Text(compute="_compute_calculation_result_field")

    @api.depends("resource_ref")
    def _compute_calculation_result_field(self):
        """Compute the calculation result based on resource_ref."""
        try:
            self.calculation_result = False
            if self.resource_ref:
                initial_values = {}
                result = self.env["base.calculation"].calculate(
                    self.reference, self.resource_ref, **initial_values
                )
                self.calculation_result = result
            self.error_msg = False
        except (ValueError, SyntaxError) as error:
            self.error_msg = error.args[0]
            self.calculation_result = False
