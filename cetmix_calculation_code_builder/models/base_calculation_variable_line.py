# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models


class BaseCalculationVariableLine(models.Model):
    _inherit = "base.calculation.variable.line"

    is_digit = fields.Boolean(
        related="variable_id.is_digit", index=True, store=True, readonly=True
    )
