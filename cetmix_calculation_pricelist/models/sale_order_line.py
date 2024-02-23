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
