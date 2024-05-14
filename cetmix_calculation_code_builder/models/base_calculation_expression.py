# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

import re

from odoo import api, fields, models


class BaseCalculationExpression(models.Model):
    _name = "base.calculation.expression"
    _description = "Base Calculation Expression"
    _order = "order, id desc"

    active = fields.Boolean(default=True)
    order = fields.Integer(default=10)
    name = fields.Char(
        string="Expression",
        compute="_compute_expression_name",
        store=True,
        precompute=True,
    )
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

    @api.depends("rule_ids")
    def _compute_expression_name(self):
        """Compute expression name"""
        for rec in self:
            rec.name = rec._prepare_expression_name()

    @api.onchange("rule_ids")
    def onchange_rules(self):
        """Compute rule name before saving"""
        for rec in self:
            rec.rule_ids._compute_rule_name()

    def get_variable_value(self, variable_value):
        """Return a modified variable value.

        Args:
            variable_value (str): The variable value to be modified.

        Returns:
            str: The modified variable value with
            certain parts enclosed in single quotes.

        """
        # Get variables
        variables = self.env["base.calculation.variable.line"].search(
            [
                "|",
                ("calculation_id", "in", self.calculation_block_id.calculation_ids.ids),
                ("calculation_id", "=", False),
            ]
        )

        # Define a set of keys that should not be enclosed in single quotes
        special_keys = {
            "uid",
            "user",
            "time",
            "datetime",
            "dateutil",
            "timezone",
            "float_compare",
            "b64encode",
            "b64decode",
            "Command",
            "env",
            "model",
            "Warning",
            "UserError",
            "records",
            "log",
            "RESULT",
        }

        # Construct regex pattern for splitting based on operators
        operators = [
            "+",
            "-",
            "*",
            "/",
            "**",
            "//",
            "%",
        ]
        operator_pattern = "|".join(re.escape(op) for op in operators)
        parts = re.split(f"({operator_pattern})", variable_value)

        # Check each part if it's a variable name, operator, number, or special key
        for i, part in enumerate(parts):
            # Check if the part is an operator or number
            if part.strip() in operators or part.strip().isdigit():
                continue
            # Check if the part is a special key
            elif part.strip() in special_keys:
                continue
            # Check if the part is a variable name
            elif part.strip() in [variable.variable_name for variable in variables]:
                continue
            else:
                # Wrap it in single quotes
                parts[i] = f" '{part.strip()}'"

        # Join the parts back together into a single string
        return "".join(parts)

    def get_result_as_variables(self):
        return "for key, value in RESULT.items():\n\tlocals()[key] = value\n"

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
                expression_result += self.get_result_as_variables()
                expression_result += expression.rule_ids.generate_if_cases()
                for variable_line in expression.variable_line_ids:
                    variable_value = self.get_variable_value(variable_line.value)
                    expression_result += (
                        f"\t{variable_line.variable_name} = {variable_value}\n"
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
