# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo import api, fields, models

from .states import (
    CONDITION,
)


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
        condition_string_rule = ""
        for rule in self:
            if condition_string_rule:
                condition_string_rule += " or "
            condition_string = ""
            for condition in rule.condition_ids:
                if condition_string:
                    condition_string += " and "
                condition_string += self.get_condition_string(condition)
            condition_string_rule += f"({condition_string})"
        if_cases = f"if {condition_string_rule}:\n"
        return if_cases

    def get_condition_string(self, condition):
        """
        Get the string representation of a condition.

        Args:
            condition (Record): The condition record.

        Returns:
            str: The string representation of the condition.
        """
        if condition.condition == "like":
            return f"'{condition.value}' in {condition.variable_id.name}"
        elif condition.condition == "not_like":
            return f"'{condition.value}' not in {condition.variable_id.name}"
        elif condition.condition == "in":
            values_list = [value.strip() for value in condition.value.split(",")]
            values_str = ", ".join([f"'{value}'" for value in values_list])
            return f"{condition.variable_id.name} in [{values_str}]"
        elif condition.condition in CONDITION:
            operator_string = condition.condition
            return f"{condition.variable_id.name} {operator_string} '{condition.value}'"
        else:
            return ""
