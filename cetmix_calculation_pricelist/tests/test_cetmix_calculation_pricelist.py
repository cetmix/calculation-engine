# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
from odoo.addons.base.tests.common import BaseCommon


class TestCetmixCalculationPricelist(BaseCommon):
    """Test Cetmix Calculatio nPricelist"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.calculation_obj = cls.env["base.calculation"]
        cls.calculation_block_obj = cls.env["base.calculation.block"]
        cls.calculation_line_obj = cls.env["base.calculation.line"]
        cls.calculation_variable_obj = cls.env["base.calculation.variable"]
        cls.calculation_variable_line_obj = cls.env["base.calculation.variable.line"]
        pricelist_item_model = cls.env["ir.model"].search(
            [("model", "=", "product.pricelist.item")]
        )
        cls.calculation = cls.calculation_obj.create(
            {
                "name": "Test Caclulation",
                "reference": "TEST_CALCULATION",
                "model_id": pricelist_item_model.id,
            }
        )
        cls.calculation_block_1 = cls.calculation_block_obj.create(
            {
                "name": "Test Caclulation Block 1",
                "reference": "TEST_CALCULATION_BLOCK",
            }
        )
        cls.calculation_block_1.write(
            {
                "expression": """RESULT["PRICE_TOTAL"] = 45.0""",
            }
        )
        cls.calculation_line_1 = cls.calculation_line_obj.create(
            {
                "calculation_id": cls.calculation.id,
                "block_id": cls.calculation_block_1.id,
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 100,
                "standard_price": 50,
            }
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Test Pricelist", "discount_policy": "without_discount"}
        )
        cls.pricelist_rule = cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist.id,
                "applied_on": "0_product_variant",
                "product_id": cls.product.id,
                "compute_price": "formula",
                "base": "list_price",
                "calculation_id": cls.calculation.id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": cls.pricelist.id,
            }
        )

    def test_compute_price(self):
        """Test _compute_price"""
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "product_id": self.product.id,
                "product_uom_qty": 100,
            }
        )

        sale_order_line_price = self.pricelist_rule._compute_price(
            self.product,
            order_line.product_uom_qty,
            order_line.product_uom,
            order_line.create_date,
        )

        self.assertEqual(
            sale_order_line_price,
            45.0,
            "The Price unit is wrong.",
        )
