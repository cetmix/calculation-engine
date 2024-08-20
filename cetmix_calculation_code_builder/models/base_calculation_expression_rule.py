# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

import logging

from odoo import api, fields, models

from .states import (
    CONDITION,
)
from .utils import inline_and, inline_or

_logger = logging.getLogger(__name__)


class BaseCalculationExpressionRule(models.Model):
    _name = "base.calculation.expression.rule"
    _description = "Base Calculation Expression Rule"
    _order = "id desc"

    name = fields.Char("Condition", compute="_compute_rule_name")

    expression_id = fields.Many2one(
        "base.calculation.expression", string="Expression", ondelete="cascade"
    )
    condition_ids = fields.One2many("base.calculation.expression.condition", "rule_id")

    def _prepare_rule_name(self):
        """Prepare rule name"""
        self.ensure_one()
        return " AND ".join(self.condition_ids.mapped("name"))

    def _compute_rule_name(self):
        """Compute rule name"""
        for rec in self:
            rec.name = rec._prepare_rule_name()

    @api.onchange("condition_ids")
    def onchange_conditions(self):
        """Recompute condition name"""
        for rec in self:
            rec.condition_ids._compute_condition_name()

    def generate_if_cases(self):
        """
        Generate if cases based on condition rules.

        Returns:
            str: The generated if cases.
        """
        condition_string_rules = []
        for rule in self:
            condition_strings = [
                self.get_condition_string(condition) for condition in rule.condition_ids
            ]
            condition_string = inline_and(condition_strings)
            condition_string_rules.append(f"({condition_string})")

        condition_string_rule = inline_or(condition_string_rules)
        return f"if {condition_string_rule}:\n" if condition_string_rule else False

    def get_condition_string(self, condition):
        """
        Get the string representation of a condition.

        Args:
            condition (Record): The condition record.

        Returns:
            str: The string representation of the condition.
        """
        try:
            if condition.condition in ["like", "not_like"]:
                if condition.variable_id.is_digit:
                    value_str = str(float(condition.value))
                else:
                    value_str = f"'{condition.value}'"
                if condition.condition == "like":
                    return f"{value_str} in {condition.variable_id.name}"
                elif condition.condition == "not_like":
                    return f"{value_str} not in {condition.variable_id.name}"
            elif condition.condition in ["in", "not_in"]:
                values_list = [value.strip() for value in condition.value.split(",")]
                if condition.variable_id.is_digit:
                    values_str = ", ".join([str(float(value)) for value in values_list])
                else:
                    values_str = ", ".join([f"'{value}'" for value in values_list])
                if condition.condition == "in":
                    return f"{condition.variable_id.name} in ({values_str})"
                elif condition.condition == "not_in":
                    return f"{condition.variable_id.name} not in ({values_str})"
            elif condition.condition == "is_not_set":
                return f"not {condition.variable_id.name}"
            elif condition.condition == "is_set":
                return f"{condition.variable_id.name}"
            elif condition.condition in CONDITION:
                operator_string = condition.condition
                if condition.variable_id.is_digit:
                    value_str = str(float(condition.value))
                else:
                    value_str = f"'{condition.value}'"
                return f"{condition.variable_id.name} {operator_string} {value_str}"
            else:
                return ""
        except Exception as e:
            error_message = f"Error: {str(e)}"
            _logger.warning(error_message)
            return ""
