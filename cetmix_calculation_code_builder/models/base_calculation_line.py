# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class BaseCalculationLine(models.Model):
    _inherit = "base.calculation.line"

    expression_ids = fields.One2many(
        comodel_name="base.calculation.expression", inverse_name="calculation_line_id"
    )

    condition = fields.Char(compute="_compute_condition", store=True, readonly=False)

    @api.depends("expression_ids.rule_ids", "expression_ids.rule_ids.condition_ids")
    def _compute_condition(self):
        """Compute the condition field based on the related expression's rules."""
        for record in self:
            if record.expression_ids:
                record.condition = record.expression_ids[
                    0
                ].get_expression_builder_condition()
            else:
                record.condition = False

    @api.constrains("expression_ids")
    def _check_unique_expression(self):
        """Ensure each Calculation Line is linked to only one Expression."""
        for record in self:
            if len(record.expression_ids) > 1:
                raise ValidationError(
                    _("A Calculation Line can only be linked to one Expression.")
                )

    def action_show_expression_builder_condition(self):
        """Open the Expression Builder form view for the related Expression."""
        self.ensure_one()
        view = self.env.ref(
            "cetmix_calculation_code_builder.base_calculation_line_expression_view_form"
        )

        res_id = self.expression_ids[0].id if self.expression_ids else False
        return {
            "name": _("Expression Builder Condition"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "base.calculation.expression",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": res_id,
            "context": dict(
                self.env.context,
                default_calculation_line_id=self.id,
                form_view_initial_mode="edit" if res_id else "create",
            ),
        }
