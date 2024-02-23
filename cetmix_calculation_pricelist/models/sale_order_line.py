# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_pricelist_price(self):
        return super(
            SaleOrderLine,
            self.with_context(sale_order_line=self),
        )._get_pricelist_price()

    def _get_initial_values(self):
        """
        Retrieves the initial values based on the current order line.

        Returns:
            dict: A dictionary with initial values:
                - ORDER: The sale order.
                - ORDER_LINE: The sale order line.
                - CUSTOMER: The customer.
                - RECIPIENT: The shipping recipient.
                - PAYER: The invoice payer.
        """
        order_line = self if self else False
        order = order_line.order_id if order_line else False

        return {
            "ORDER": order,
            "ORDER_LINE": order_line,
            "CUSTOMER": order.partner_id if order else False,
            "RECIPIENT": order.partner_shipping_id if order else False,
            "PAYER": order.partner_invoice_id if order else False,
        }
