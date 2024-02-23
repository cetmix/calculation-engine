# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import test_python_expr


class BaseCalculationBlock(models.Model):
    _name = "base.calculation.block"
    _description = "Base Calculation Block"
    _rec_name = "name"

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

    name = fields.Char(required=True)
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
    line_ids = fields.One2many(
        string="Lines",
        comodel_name="base.calculation.line",
        inverse_name="block_id",
        auto_join=True,
    )
    calculation_ids = fields.Many2many(
        "base.calculation", compute="_compute_calculation_ids"
    )
    calculation_count = fields.Integer(compute="_compute_calculation_count")

    @api.depends("line_ids")
    def _compute_calculation_ids(self):
        for block in self:
            block.calculation_ids = [(6, 0, block.line_ids.calculation_id.ids)]

    @api.depends("calculation_ids")
    def _compute_calculation_count(self):
        for block in self:
            block.calculation_count = len(block.calculation_ids)

    @api.constrains("expression")
    def _check_python_expression(self):
        for record in self.sudo().filtered("expression"):
            msg = test_python_expr(expr=record.expression.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    @api.model
    def create(self, vals):
        reference = vals.get("reference", False)
        if reference and not re.match(r"^[A-Z0-9_]+$", reference):
            vals.update({"reference": self._auto_correct_reference(reference)})
        return super().create(vals)

    def write(self, vals):
        reference = vals.get("reference", False)
        if reference and not re.match(r"^[A-Z0-9_]+$", reference):
            vals.update({"reference": self._auto_correct_reference(reference)})
        return super().write(vals)

    def _auto_correct_reference(self, reference):
        """Auto-corrects the reference to match the specified pattern."""
        corrected = re.sub(r"[^A-Z0-9_]", "", reference.replace(" ", "_").upper())
        return corrected

    def action_view_related_calculations(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Calculations",
            "view_mode": "tree,form",
            "res_model": "base.calculation",
            "domain": [("id", "in", self.calculation_ids.ids)],
            "context": {"default_block_id": self.id},
        }
