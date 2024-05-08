# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo import api, fields, models


class BaseCalculationExpression(models.Model):
    _name = "base.calculation.expression"
    _description = "Base Calculation Expression"
    _order = "order, id desc"

    active = fields.Boolean(default=True)
    order = fields.Integer(default=10)
    name = fields.Char(string="Expression", compute="_compute_expression_name")
    rule_ids = fields.One2many(
        comodel_name="base.calculation.expression.rule", inverse_name="expression_id"
    )
    calculation_block_id = fields.Many2one(
        "base.calculation.block", ondelete="cascade", required=True
    )
    variable_line_ids = fields.One2many(
        string="Variables",
        comodel_name="base.calculation.expression.variable.line",
        inverse_name="expression_id",
        auto_join=True,
    )
    variable_ids = fields.Many2many(
        comodel_name="base.calculation.variable",
        relation="base_calculation_variable_expression_rel",
        column1="expression_id",
        column2="variable_id",
        required=True,
        string="Add Variables to Result",
    )

    def _prepare_expression_name(self):
        """Prepare expression name"""
        self.ensure_one()
        return " OR ".join(self.rule_ids.mapped("name"))

    def _compute_expression_name(self):
        """Compute expression name"""
        for rec in self:
            rec.name = rec._prepare_expression_name()

    @api.onchange("rule_ids")
    def onchange_rules(self):
        """Compute rule name before saving"""
        for rec in self:
            rec.rule_ids._compute_rule_name()

    def get_expression_builder_result(self):
        """
        Get the result of the expression builder.

        Returns:
            str: The result of the expression builder.
        """
        expression_result = ""
        variables_result_names = []
        for expression in self:
            if expression.variable_line_ids:
                expression_result += expression.rule_ids.generate_if_cases()
                for variable_line in expression.variable_line_ids:
                    expression_result += (
                        f"\t{variable_line.variable_name} = {variable_line.value}\n"
                    )
            variables_result_names.extend(
                [variable.name for variable in expression.variable_ids]
            )
        expression_result += "\n".join(
            [
                f"RESULT['{variable_name}'] = {variable_name}"
                for variable_name in variables_result_names
            ]
        )
        return expression_result
