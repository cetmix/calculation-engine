# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

import base64
import re

from pytz import timezone

from odoo import Command, _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare
from odoo.tools.safe_eval import safe_eval


class BaseCalculation(models.Model):
    _name = "base.calculation"
    _description = "Base Calculation"

    name = fields.Char(required=True)
    reference = fields.Char(
        required=True,
        help="This is a unique reference of the Calculation "
        "that will be used in expressions. Must contain "
        "CAPITAL_LETTERS_NUMBERS_EG_1_AND_UNDERSCORES_ONLY",
    )
    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        required=True,
        ondelete="cascade",
        index=True,
        help="Base model used by the Calculation.",
    )
    model = fields.Char(
        "Related Document Model",
        related="model_id.model",
        index=True,
        store=True,
        readonly=True,
    )
    block_ids = fields.One2many(
        string="Blocks",
        comodel_name="base.calculation.block",
        inverse_name="calculation_id",
        auto_join=True,
    )
    variable_ids = fields.One2many(
        string="Variables",
        comodel_name="base.calculation.variable.line",
        inverse_name="calculation_id",
        auto_join=True,
    )
    active = fields.Boolean(default=True)

    @api.constrains("reference")
    def _check_reference_format(self):
        for record in self:
            if record.reference:
                if not re.match(r"^[A-Z0-9_]+$", record.reference):
                    raise ValidationError(
                        _(
                            "Reference must contain only capital letters, "
                            "numbers, and underscores."
                        )
                    )

    def _get_eval_context(self, records=None):
        """Prepare the context used when evaluating python code.

        Args:
            records (recordset): Records passed to the calculation method.
            initial_values (dict): Additional initial values for evaluation.

        Returns:
            dict: Evaluation context
        """

        def log(message, level="info"):
            with self.pool.cursor() as cr:
                cr.execute(
                    """
                    INSERT INTO ir_logging(
                        create_date, create_uid, type, dbname, name,
                        level, message, path, line, func
                    )
                    VALUES (
                        NOW() at time zone 'UTC',
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        self.env.uid,
                        "server",
                        self._cr.dbname,
                        __name__,
                        level,
                        message,
                        "calculation",
                        self.id,
                        self.name,
                    ),
                )

        model_name = self.model
        model = self.env[model_name]
        eval_context = {
            "uid": self._uid,
            "user": self.env.user,
            "time": tools.safe_eval.time,
            "datetime": tools.safe_eval.datetime,
            "dateutil": tools.safe_eval.dateutil,
            "timezone": timezone,
            "float_compare": float_compare,
            "b64encode": base64.b64encode,
            "b64decode": base64.b64decode,
            "Command": Command,
            # orm
            "env": self.env,
            "model": model,
            # Exceptions
            "Warning": Warning,
            "UserError": UserError,
            # records
            "records": records,
            # helpers
            "log": log,
            "RESULT": {},
        }
        return eval_context

    def calculate(self, reference, records_to_process, **initial_values):
        """
        Perform calculation based on the given reference, records and initial values

        Args:
            reference (str): The reference of the calculation.
            records_to_process (recordset): Records to be processed in the calculation.
            **initial_values: Additional initial values for the calculation.

        Returns:
            list: Results for each record obtained from each calculation block.
        """
        # Find the calculation based on the provided reference
        calculation = self.search([("reference", "=", reference)], limit=1)
        if not calculation:
            raise ValidationError(
                _(f"Calculation not found for reference: {reference}")
            )

        result = []

        # Initialize variables dictionary with values from calculation
        variables = {
            record.variable_id.name: int(record.value)
            if record.value.isdigit()
            else float(record.value)
            if record.value.replace(".", "", 1).isdigit()
            else record.value
            for record in calculation.variable_ids
        }
        variables.update(initial_values)

        # Construct evaluation context
        eval_context = calculation._get_eval_context(records_to_process)

        # Evaluate expressions for each record
        for record in records_to_process:
            # Evaluate each variable expression in the variables dictionary
            eval_context["record"] = record
            evaluated_variables = dict()
            for key, expr in variables.items():
                try:
                    evaluated_variables[key] = safe_eval(expr, {}, eval_context)
                except Exception:
                    evaluated_variables[key] = expr
            evaluated_variables.update(eval_context)
            result.append(calculation.block_ids.calculate_block(evaluated_variables))
        return result
