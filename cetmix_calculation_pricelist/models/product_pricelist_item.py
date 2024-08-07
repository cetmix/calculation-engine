# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.exceptions import ValidationError


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    calculation_id = fields.Many2one("base.calculation", copy=True)

    def _compute_price(self, product, quantity, uom, date, currency=None):
        """
        - Calls superclass method to compute the base price.
        - If a calculation_id exists, gathers initial values.
        - Executes the calculation.
        - Validates 'PRICE_TOTAL' key existence; raises error if absent.

        Args:
            product: The product object.
            quantity: The quantity of the product.
            uom: The unit of measure object.
            date: The date of calculation.
            currency: The currency object (optional).

        Returns:
            float: The computed price.

        Raises:
            ValidationError: If 'PRICE_TOTAL' key is not assigned in the calculation.
        """
        result = super()._compute_price(product, quantity, uom, date, currency)
        if self.calculation_id:
            order_line = (
                self.env.context["sale_order_line"]
                if "sale_order_line" in self.env.context
                else self.env["sale.order.line"]
            )
            initial_values = order_line._get_initial_values()
            initial_values["BASE_PRICE"] = result
            initial_values["SURCHARGE"] = self.price_surcharge

            result_calculation = self.calculation_id.calculate(self, **initial_values)
            if "PRICE_TOTAL" not in result_calculation[str(self.id)]:
                raise ValidationError(
                    _(
                        f"The RESULT Key 'PRICE_TOTAL' is not assigned in the "
                        f"calculation with ID: {self.calculation_id.id} connected to "
                        f"the Pricelist Item: {self.name}."
                    )
                )
            result = result_calculation[str(self.id)]["PRICE_TOTAL"]
        return result
