# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

import base64

from pytz import timezone

from odoo import Command, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
from odoo.tools.safe_eval import safe_eval


class BaseCalculation(models.Model):
    _inherit = "base.calculation.ref.mixin"
    _name = "base.calculation"
    _description = "Base Calculation"

    model_id = fields.Many2one(
        "ir.model",
        required=True,
        ondelete="cascade",
        index=True,
        help="Base model used by the Calculation.",
    )
    model = fields.Char(
        "Related Document Model Name",
        related="model_id.model",
        index=True,
        store=True,
        readonly=True,
    )
    line_ids = fields.One2many(
        string="Lines",
        comodel_name="base.calculation.line",
        inverse_name="calculation_id",
        auto_join=True,
    )
    variable_line_ids = fields.One2many(
        string="Variables",
        comodel_name="base.calculation.variable.line",
        inverse_name="calculation_id",
        auto_join=True,
    )
    active = fields.Boolean(default=True)

    def _get_eval_context(self, records=None):
        """Prepare the context used when evaluating python code.

        Args:
            records (recordset): Records passed to the calculation method.
            initial_values (dict): Additional initial values for evaluation.

        Returns:
            dict: Evaluation context
        """

        def log(message, level="info"):
            """
            Inserts a log entry into `ir_logging` with the given message and level.

            Args:
                message (str): Log message.
                level (str): Log level, defaults to 'info'.
            """
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

    def calculate(self, records_to_process, **initial_values):
        """
        Perform calculation based on the given reference, records and initial values

        Args:
            reference (str): The reference of the calculation.
            records_to_process (recordset): Records to be processed in the calculation.
            **initial_values: Additional initial values for the calculation.

        Returns:
            result (dict): Results for each record obtained from each calculation line
            Ex: {'record_id': {calculation_result}...}
            NB: 'record_id' is String
        """
        result = dict()

        # Initialize variables dictionary with values from calculation
        variables = {
            record.variable_name: int(record.value)
            if record.value.isdigit()
            else float(record.value)
            if record.value.replace(".", "", 1).isdigit()
            else record.value
            for record in self.variable_line_ids
        }
        variables.update(initial_values)

        # Construct evaluation context
        eval_context = self._get_eval_context(records_to_process)

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
            result[str(record.id)] = self.line_ids.calculate_line(evaluated_variables)
        return result
