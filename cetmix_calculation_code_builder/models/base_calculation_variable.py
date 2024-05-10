# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models


class BaseCalculationVariable(models.Model):
    _inherit = "base.calculation.variable"

    is_digit = fields.Boolean(
        string="Digit",
        help="Set this field to True if the variable represents"
        " a numeric value, such as an integer or float.",
    )
