# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).


import keyword
import re

from odoo import api, fields, models


class BaseCalculationVariable(models.Model):
    _name = "base.calculation.variable"
    _description = "Base Calculation Variable"

    name = fields.Char(required=True)
    note = fields.Text()

    def _normalize_variable_name(self, name):
        """
        Converts a given string `name` into a PEP 8 compliant variable name.

        Args:
            name (str): The original variable name to be normalized.

        Returns:
            str: A normalized variable name that is PEP 8 compliant,
            avoiding Python keywords, and not starting with digits or
            consisting solely of invalid characters.
        """

        # Check for a potential constant: all uppercase without
        # invalid characters or leading digits
        is_potential_constant = name.isupper() and not re.search(r"\W|^\d", name)
        if is_potential_constant:
            # Return constants directly without modification
            return name

        # Replace non-alphanumeric characters with underscores and convert to lowercase
        normalized_name = re.sub(r"\W", "_", name).lower()

        # Check if the name is reduced to only underscores
        if set(normalized_name) == {"_"}:
            normalized_name = "var_default"

        # Remove leading and trailing underscores to clean up the name
        normalized_name = normalized_name.strip("_")

        # Ensure the name starts with an alphabet and is not Python reserved keyword
        if not normalized_name[0].isalpha() or keyword.iskeyword(normalized_name):
            normalized_name = "var_" + normalized_name

        return normalized_name

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overrides the create method to normalize the variable 'name' in each record.

        Args:
            vals_list (list): List of dictionaries representing records to create,
            where each dict may contain a 'name' key to normalize.

        Returns:
            Recordset: The created records with normalized 'name'.
        """
        for vals in vals_list:
            name = vals.get("name", False)
            if name:
                vals.update({"name": self._normalize_variable_name(name)})
        return super().create(vals_list)

    def write(self, vals):
        """
        Overrides the write method to normalize the variable 'name' before updating.

        Args:
            vals (dict): Dictionary of fields to update, possibly including 'name'.

        Returns:
            Result of the super `write` call.
        """
        name = vals.get("name", False)
        if name:
            vals["name"] = self._normalize_variable_name(name)
        return super().write(vals)


class BaseCalculationVariableLine(models.Model):
    _name = "base.calculation.variable.line"
    _description = "Base Calculation Variable Line"

    variable_id = fields.Many2one(
        "base.calculation.variable", ondelete="cascade", required=True
    )
    variable_name = fields.Char(
        related="variable_id.name", index=True, store=True, readonly=True
    )
    value = fields.Char(
        groups="base.group_system",
        help="This field allows you to specify a variable value "
        "as python code. Ex.1: record.city, Ex.2: 10, Ex.3: 'draft'",
    )
    calculation_id = fields.Many2one("base.calculation", ondelete="cascade")
