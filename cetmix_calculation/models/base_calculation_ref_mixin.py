# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class BaseCalculationRefMixin(models.AbstractModel):
    _name = "base.calculation.ref.mixin"
    _description = "Base Calculation Ref Mixin"
    _rec_name = "name"

    name = fields.Char(required=True)
    reference = fields.Char(
        help="This is a unique reference of the Calculation Block "
        "that will be used in expressions. Must contain "
        "CAPITAL_LETTERS_NUMBERS_EG_1_AND_UNDERSCORES_ONLY",
        index=True,
        copy=False,
    )

    _sql_constraints = [
        ("reference_unique", "UNIQUE(reference)", "The reference must be unique.")
    ]

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

    def _get_reference_pattern(self):
        """
        Returns the regex pattern used for validating and correcting references.

        This allows for easy modification of the pattern in one place.

        Returns:
            str: A regex pattern
        """
        return r"A-Z0-9_"

    def _auto_correct_reference(self, reference):
        """
        Auto-corrects the reference to match the specified pattern.

        Args:
            reference (str): Original reference.

        Returns:
            str: Corrected reference.
        """
        pattern = self._get_reference_pattern()
        corrected = re.sub(f"[^{pattern}]", "", reference.replace(" ", "_").upper())
        return corrected

    def _reference_is_valid(self, reference):
        """
        Checks if the given reference string is valid based on a specific pattern.

        A valid reference must only contain uppercase letters, digits, and underscores.

        Args:
            reference (str): The reference string to validate.

        Returns:
            bool: True if the reference is valid, False otherwise.
        """
        pattern = self._get_reference_pattern()
        return bool(re.match(f"^[{pattern}]+$", reference))

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overrides create to ensure 'reference' is auto-corrected
        or validated for each record.

        Args:
            vals_list (list[dict]): List of dictionaries with record values.

        Returns:
            Records: The created record(s).
        """
        for vals in vals_list:
            reference = vals.get("reference", False)
            if not reference:
                vals.update(
                    {"reference": self._auto_correct_reference(vals.get("name"))}
                )
            if reference and not self._reference_is_valid(reference):
                vals.update({"reference": self._auto_correct_reference(reference)})
        return super().create(vals_list)

    def write(self, vals):
        """
        Updates record, auto-correcting or validating 'reference'
        based on 'name' or existing value.

        Args:
            vals (dict): Values to update, may include 'reference'.

        Returns:
            Result of the super `write` call.
        """
        reference = vals.get("reference", False)
        if not reference:
            vals.update({"reference": self._auto_correct_reference(self.name)})
        if reference and not self._reference_is_valid(reference):
            vals.update({"reference": self._auto_correct_reference(reference)})
        return super().write(vals)

    def _get_copied_name(self):
        """
        Return a copied name of the base.calculation.ref.mixin record
        by adding the suffix (copy) at the end
        and counter until the name is unique.

        Returns:
            An unique name for the copied base.calculation.ref.mixin
        """
        self.ensure_one()
        original_name = self.name
        copy_name = _(f"{original_name} (Copy)")
        counter = 1
        while self.search_count([("name", "=", copy_name)]) > 0:
            counter += 1
            copy_name = _(f"{original_name} (Copy {counter})")
        return copy_name

    def copy(self, default=None):
        """
        Overrides the copy method to ensure unique reference values
        for duplicated records.

        Args:
            default (dict, optional): Default values for the new record.

        Returns:
            Record: The newly copied record with adjusted defaults.
        """
        self.ensure_one()
        if default is None:
            default = {}
        default["name"] = self._get_copied_name()
        if "reference" not in default:
            default["reference"] = self._auto_correct_reference(default["name"])
        return super().copy(default=default)

    def get_by_reference(self, reference):
        """
        Retrieves the first calculation matching the given reference.

        Args:
            reference (str): The reference string to search for.

        Returns:
            dict: The first calculation found matching the reference.

        Raises:
            ValidationError: If no calculation is found matching the reference.
        """
        calculation = self.search([("reference", "=", reference)], limit=1)
        if not calculation:
            raise ValidationError(
                _(f"Calculation not found for reference: {reference}")
            )
        return calculation
