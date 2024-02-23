# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

import re
from copy import deepcopy

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval, test_python_expr


class BaseCalculationBlock(models.Model):
    _name = "base.calculation.block"
    _description = "Base Calculation Block"
    _order = "sequence"

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

    sequence = fields.Integer(default=10)
    reference = fields.Char(
        required=True,
        help="This is a unique reference of the Calculation Block "
        "that will be used in expressions. Must contain "
        "CAPITAL_LETTERS_NUMBERS_EG_1_AND_UNDERSCORES_ONLY",
    )
    expression = fields.Text(
        string="Python Expression",
        default=DEFAULT_PYTHON_CODE,
        help="Python expression. Must assign a value to the "
        "built-in RESULT variable.",
    )
    condition = fields.Char(
        help="This field allows you to specify a condition as "
        "python code that determines in which case the expression "
        "will be executed. Please enter the condition using "
        "the appropriate syntax. Example: "
        "SALE_TOTAL > 10000 and CITY_NAME.upper() == 'NEW YORK'"
    )
    calculation_id = fields.Many2one("base.calculation", ondelete="cascade")

    @api.constrains("reference")
    def _check_reference_format(self):
        for record in self:
            if record.reference:
                if not re.match(r"^[A-Z0-9_]+$", record.reference):
                    raise ValidationError(
                        _(
                            "Reference must contain only capital letters, "
                            "numbers, and underscores."
                        )
                    )

    @api.constrains("condition")
    def _check_python_condition(self):
        for record in self.sudo().filtered("condition"):
            msg = test_python_expr(expr=record.condition.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    @api.constrains("expression")
    def _check_python_expression(self):
        for record in self.sudo().filtered("expression"):
            msg = test_python_expr(expr=record.expression.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    def calculate_block(self, variables):
        """
        Evaluate condition and expression within calculation blocks
        based on the provided variables.

        Args:
            variables (dict): Dictionary containing variables to be used in evaluation.

        Returns:
            dict: Dictionary containing the results obtained
            from evaluating expressions.
        """
        result = dict()
        for calculation_block in self:
            # Check if condition is satisfied
            if calculation_block.condition:
                if safe_eval(calculation_block.condition, variables):
                    # Evaluate expression
                    safe_eval(calculation_block.expression, variables, mode="exec")
                    result_dict = deepcopy(variables.get("RESULT", {}))
                    result.update(result_dict)
            else:
                # Evaluate expression
                safe_eval(calculation_block.expression, variables, mode="exec")
                result_dict = deepcopy(variables.get("RESULT", {}))
                result.update(result_dict)
        return result
