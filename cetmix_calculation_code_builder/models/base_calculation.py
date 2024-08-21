# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).


from odoo import models


class BaseCalculation(models.Model):
    _inherit = "base.calculation"

    def _get_eval_context(self, records=None):
        """Prepare the context used when evaluating python code.
        This method extends the evaluation context provided by the superclass
        to include locals.

        Args:
            records (recordset): Records passed to the calculation method.

        Returns:
            dict: Evaluation context
        """
        result = super()._get_eval_context(records=records)
        result["locals"] = locals  # the locals() built-in method
        return result
