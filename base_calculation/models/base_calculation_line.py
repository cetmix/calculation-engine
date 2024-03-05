# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from copy import deepcopy

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
