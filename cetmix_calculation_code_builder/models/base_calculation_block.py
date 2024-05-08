# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo import api, fields, models


class BaseCalculationBlock(models.Model):
    _inherit = "base.calculation.block"

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

    use_expressions = fields.Boolean(
        help="This checkbox allows you to build calculations directly from the UI "
        "without needing to write Python code. It utilizes Expression Blocks, "
        "which are automatically converted into Python code."
    )
    expression_ids = fields.One2many(
        comodel_name="base.calculation.expression", inverse_name="calculation_block_id"
    )
    expression = fields.Text(compute="_compute_expression", store=True)

    @api.depends("use_expressions", "expression_ids")
    def _compute_expression(self):
        for record in self:
            if record.use_expressions:
                record.expression = (
                    record.expression_ids.get_expression_builder_result()
                )
            else:
                record.expression = record.DEFAULT_PYTHON_CODE

    @api.onchange("expression_ids")
    def onchange_expression_ids(self):
        """Compute expression name before saving"""
        for rec in self:
            rec.expression_ids._compute_expression_name()
