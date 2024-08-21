# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo import api, fields, models


class BaseCalculationBlock(models.Model):
    _inherit = "base.calculation.block"

    DEFAULT_PYTHON_CODE = """# Available variables:
    #  - env: Odoo Environment on which the calculation is triggered
    #  - model: Odoo Model of the record on which the calculation is triggered;
    #  is a void recordset
    #  - record: record on which the calculation is triggered; may be void
    #  - records: recordset of all records on which the calculation
    #  is triggered in multi-mode; may be void
    #  - time, datetime, dateutil, timezone: useful Python libraries
    #  - float_compare: Odoo function to compare floats based on specific precisions
    #  - log: log(message, level='info'): logging function to
    #  record debug information in ir.logging table
    #  - UserError: Warning Exception to use with raise
    #  - Command: x2Many commands namespace
    # To return a RESULT, assign: RESULT["key_name"] = ...
    # Ex: RESULT["final_price"] = SALE_TOTAL * discount_multiplier\n\n\n\n"""

    use_expressions = fields.Boolean(
        string="Expression Builder",
        help="This checkbox allows you to build calculations directly from the UI "
        "without needing to write Python code. It utilizes Expression Blocks, "
        "which are automatically converted into Python code.",
    )
    expression_ids = fields.One2many(
        comodel_name="base.calculation.expression", inverse_name="calculation_block_id"
    )
    expression = fields.Text(compute="_compute_expression", store=True)

    @api.depends("use_expressions", "expression_ids")
    def _compute_expression(self):
        for record in self:
            if record.use_expressions:
                record.expression = record.get_expression_builder_result()
            else:
                record.expression = record.DEFAULT_PYTHON_CODE

    @api.onchange("expression_ids")
    def onchange_expression_ids(self):
        """Compute expression name before saving"""
        for rec in self:
            rec.expression_ids._compute_expression_name()

    def get_expression_builder_result(self):
        """
        Get the result of the expression builder.

        Returns:
            str: The result of the expression builder.
        """
        self.ensure_one()
        expression_result = self.env[
            "base.calculation.expression"
        ].get_result_as_variables()
        variable_lines = self.expression_ids.get_variable_lines()
        variables = variable_lines.mapped("variable_id") if variable_lines else False

        variables_result_names = []
        default_variable_names = set()
        variables_default_value = ""
        for expression in self.expression_ids:
            if expression.variable_line_ids:
                if_case = expression.rule_ids.generate_if_cases()
                expression_result += if_case if if_case else ""
                for variable_line in expression.variable_line_ids:
                    variable_value = expression.get_variable_value(variable_line.value)
                    indent = "\t" if if_case else ""
                    expression_result += (
                        f"{indent}{variable_line.variable_name} = {variable_value}\n"
                    )
                    if variables and variable_line.variable_id not in variables:
                        if variable_line.variable_name not in default_variable_names:
                            default_variable_names.add(variable_line.variable_name)
                            variables_default_value += (
                                f"{variable_line.variable_name} = False\n"
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
        return variables_default_value + expression_result
