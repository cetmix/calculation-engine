# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).


from odoo import fields, models


class BaseCalculationVariable(models.Model):
    _name = "base.calculation.variable"
    _description = "Base Calculation Variable"

    name = fields.Char()


class BaseCalculationVariableLine(models.Model):
    _name = "base.calculation.variable.line"
    _description = "Base Calculation Variable Line"

    variable_id = fields.Many2one("base.calculation.variable", ondelete="cascade")
    variable_name = fields.Char(
        related="variable_id.name", index=True, store=True, readonly=True
    )
    value = fields.Char(
        groups="base.group_system",
        help="This field allows you to specify a variable value "
        "as python code. Ex.1: record.city, Ex.2: 10, Ex.3: 'draft'",
    )
    calculation_id = fields.Many2one("base.calculation", ondelete="cascade")
