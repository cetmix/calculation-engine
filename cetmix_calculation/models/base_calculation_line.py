# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
import re
from copy import deepcopy
from types import SimpleNamespace

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval, test_python_expr


class BaseCalculationLine(models.Model):
    _name = "base.calculation.line"
    _description = "Base Calculation Line"
    _order = "sequence"

    sequence = fields.Integer(default=10)
    condition = fields.Char(
        help="This field allows you to specify a condition as "
        "python code that determines in which case the expression "
        "will be executed. Please enter the condition using "
        "the appropriate syntax. Example: "
        "SALE_TOTAL > 10000 and CITY_NAME.upper() == 'NEW YORK'"
    )
    block_id = fields.Many2one(
        "base.calculation.block",
        ondelete="cascade",
        help="Calculation Block that will be evaluated",
        auto_join=True,
        required=True,
    )
    calculation_id = fields.Many2one(
        "base.calculation", ondelete="cascade", required=True
    )
    reference = fields.Char(
        related="block_id.reference", store=True, readonly=True, index=True
    )

    @api.constrains("condition")
    def _check_python_condition(self):
        for record in self.sudo().filtered("condition"):
            msg = test_python_expr(expr=record.condition.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    def get_reference_result_context(self, expr, **variables):
        """
        Resolves 'CALCULATUION_BLOCK_REFERENCE.RESULT'
        in an expression to actual values.

        Scans the expression for 'CALCULATUION_BLOCK_REFERENCE.RESULT' patterns,
        retrieves corresponding calculation results, and returns a dictionary
        mapping each reference to its calculation result wrapped in SimpleNamespace.

        Args:
            expr (str): The expression containing 'CALCULATUION_BLOCK_REFERENCE.RESULT'
            variables (dict): Available variables and their values for calculations.

        Returns:
            dict: Each key is a 'CALCULATUION_BLOCK_REFERENCE' from the expression,
            mapped to a SimpleNamespace containing its 'RESULT'.
        """
        eval_context = {}

        pattern = re.compile(r"([A-Z0-9_]+)\.RESULT")
        matches = pattern.findall(expr)
        for reference in matches:
            calculation_block = self.env["base.calculation.block"].get_by_reference(
                reference
            )
            calculation_line = self.filtered(
                lambda calc_line,
                calc_block=calculation_block: calc_line.block_id.reference
                == calc_block.reference
            )
            # Make a deep copy of 'RESULT' to avoid modifications
            result_dict = deepcopy(variables.get("RESULT", {}))
            result = calculation_line.calculate_line(variables)
            eval_context[f"{reference}"] = SimpleNamespace(RESULT=result)
            eval_context["RESULT"] = result_dict
        return eval_context

    def calculate_line(self, variables):
        """
        Evaluate condition and expression within calculation lines
        based on the provided variables.

        Args:
            variables (dict): Dictionary containing variables to be used in evaluation.

        Returns:
            result (dict): Dictionary containing the results obtained
            from evaluating expressions.
        """
        result = dict()
        for calculation_line in self:
            reference_context = self.get_reference_result_context(
                calculation_line.block_id.expression, **variables
            )
            variables.update(reference_context)
            # Check if condition is satisfied
            if calculation_line.condition:
                if safe_eval(calculation_line.condition, variables):
                    # Evaluate expression
                    safe_eval(
                        calculation_line.block_id.expression, variables, mode="exec"
                    )
                    result_dict = deepcopy(variables.get("RESULT", {}))
                    result.update(result_dict)
            else:
                # Evaluate expression
                safe_eval(calculation_line.block_id.expression, variables, mode="exec")
                result_dict = deepcopy(variables.get("RESULT", {}))
                result.update(result_dict)
        return result
