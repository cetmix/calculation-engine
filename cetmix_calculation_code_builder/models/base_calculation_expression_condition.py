# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

import logging

from odoo import fields, models

from .states import (
    CONDITION,
)

_logger = logging.getLogger(__name__)


class BaseCalculationExpressionCondition(models.Model):
    _name = "base.calculation.expression.condition"
    _description = "Base Calculation Expression Conditions"

    name = fields.Char(string="Conditions", compute="_compute_condition_name")
    rule_id = fields.Many2one(
        "base.calculation.expression.rule", string="Filter", ondelete="cascade"
    )
    variable_id = fields.Many2one(
        "base.calculation.variable", ondelete="cascade", required=True
    )
    is_digit = fields.Boolean(
        related="variable_id.is_digit", index=True, store=True, readonly=False
    )
    value = fields.Char(string="Search text (optional)")
    condition = fields.Selection(
        [
            ("==", "is equal to"),
            ("!=", "is not equal to"),
            (">", "is greater than"),
            (">=", "is greater than or equal to"),
            ("<", "is less than"),
            ("<=", "is less than or equal to"),
            ("in", "in"),
            ("not_in", "not in"),
            ("like", "contains"),
            ("not_like", "doesn't contain"),
            ("is_set", "is set"),
            ("is_not_set", "is not set"),
        ],
        required=True,
        default="=",
    )

    def _prepare_condition_name(self):
        """Prepare condition name"""
        try:
            variable_name = self.variable_id.display_name
            condition = CONDITION.get(self.condition)
            if condition in ["contains", "doesn't contain"]:
                if self.variable_id.is_digit:
                    contains = str(float(self.value))
                else:
                    contains = f"'{self.value}'"
                return f"{variable_name} {condition} {contains}"
            elif condition in ["is in", "not in"]:
                values_list = [value.strip() for value in self.value.split(",")]
                if self.variable_id.is_digit:
                    values_str = ", ".join([str(float(value)) for value in values_list])
                else:
                    values_str = ", ".join([f"'{value}'" for value in values_list])
                return f"{variable_name} {condition} ({values_str})"
            elif condition == "is not set":
                return f"{variable_name} {condition}"
            elif condition == "is set":
                return f"{variable_name} {condition}"
            else:
                if self.variable_id.is_digit:
                    contains = str(float(self.value))
                else:
                    contains = f"'{self.value}'"
                return f"{variable_name} {condition} {contains}"
        except Exception as e:
            error_message = f"Error: {str(e)}"
            _logger.warning(error_message)
            return ""

    def _compute_condition_name(self):
        """Compute name for condition"""
        for rec in self:
            rec.name = rec._prepare_condition_name()
