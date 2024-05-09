# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models

from .states import (
    CONDITION,
)


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
            ("like", "contains"),
            ("not_like", "doesn't contain"),
        ],
        required=True,
        default="=",
    )

    def _prepare_condition_name(self):
        """Prepare condition name"""
        variable_name = self.variable_id.name
        condition = CONDITION.get(self.condition)
        contains = f"'{self.value}'"
        return f"{variable_name} {condition} {contains}"

    def _compute_condition_name(self):
        """Compute name for condition"""
        for rec in self:
            rec.name = rec._prepare_condition_name()
