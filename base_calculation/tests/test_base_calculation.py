# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
from odoo.addons.base.tests.common import BaseCommon


class TestBaseCalculation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_obj = cls.env["res.partner"]
        cls.product_obj = cls.env["product.product"]
        cls.sale_order_obj = cls.env["sale.order"]
        cls.sale_order_line_obj = cls.env["sale.order.line"]
        cls.calculation_obj = cls.env["base.calculation"]
        cls.calculation_block_obj = cls.env["base.calculation.block"]
        cls.calculation_line_obj = cls.env["base.calculation.line"]
        cls.calculation_variable_obj = cls.env["base.calculation.variable"]
        cls.calculation_variable_line_obj = cls.env["base.calculation.variable.line"]
        partner_model = cls.env["ir.model"].search([("model", "=", "res.partner")])

        # Partners
        cls.res_partner_bob = cls.partner_obj.create(
            {"name": "Bob", "city": "New York", "phone": "315-264-53229"}
        )
        cls.res_partner_mike = cls.partner_obj.create(
            {"name": "Mike", "city": "New York", "phone": "646-942-5899"}
        )
        cls.res_partner_max = cls.partner_obj.create(
            {"name": "Max", "city": "New York", "phone": "631-919-674"}
        )

        # Products
        cls.product_1 = cls.product_obj.create(
            {"name": "Meme design", "detailed_type": "product"}
        )
        cls.product_2 = cls.product_obj.create(
            {"name": "Such Much Meme", "detailed_type": "product"}
        )
        cls.product_3 = cls.product_obj.create(
            {"name": "Meme development", "detailed_type": "service"}
        )

        # Sale Orders Bob
        cls.sale_order_bob_1 = cls.sale_order_obj.create(
            {"partner_id": cls.res_partner_bob.id}
        )
        cls.order_line_bob_1 = cls.sale_order_line_obj.create(
            {
                "order_id": cls.sale_order_bob_1.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_uom_qty": 10.0,
                "price_unit": 1000.0,
            }
        )
        cls.sale_order_bob_2 = cls.sale_order_obj.create(
            {"partner_id": cls.res_partner_bob.id}
        )
        cls.order_line_bob_2 = cls.sale_order_line_obj.create(
            {
                "order_id": cls.sale_order_bob_2.id,
                "product_id": cls.product_2.id,
                "product_uom": cls.product_2.uom_id.id,
                "product_uom_qty": 25.0,
                "price_unit": 400.0,
            }
        )
        cls.order_line_bob_3 = cls.sale_order_line_obj.create(
            {
                "order_id": cls.sale_order_bob_2.id,
                "product_id": cls.product_3.id,
                "product_uom": cls.product_3.uom_id.id,
                "product_uom_qty": 20.0,
                "price_unit": 500.0,
            }
        )

        # Sale Orders Mike
        cls.sale_order_mike_1 = cls.sale_order_obj.create(
            {"partner_id": cls.res_partner_mike.id}
        )
        cls.order_line_mike_1 = cls.sale_order_line_obj.create(
            {
                "order_id": cls.sale_order_mike_1.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_uom_qty": 15.0,
                "price_unit": 1500.0,
            }
        )
        cls.sale_order_mike_2 = cls.sale_order_obj.create(
            {"partner_id": cls.res_partner_mike.id}
        )
        cls.order_line_mike_2 = cls.sale_order_line_obj.create(
            {
                "order_id": cls.sale_order_mike_2.id,
                "product_id": cls.product_2.id,
                "product_uom": cls.product_2.uom_id.id,
                "product_uom_qty": 30.0,
                "price_unit": 450.0,
            }
        )
        cls.order_line_mike_3 = cls.sale_order_line_obj.create(
            {
                "order_id": cls.sale_order_mike_2.id,
                "product_id": cls.product_3.id,
                "product_uom": cls.product_3.uom_id.id,
                "product_uom_qty": 20.0,
                "price_unit": 500.0,
            }
        )

        # Sale Order Max
        cls.sale_order_max_1 = cls.sale_order_obj.create(
            {"partner_id": cls.res_partner_max.id}
        )
        cls.order_line_max_1 = cls.sale_order_line_obj.create(
            {
                "order_id": cls.sale_order_max_1.id,
                "product_id": cls.product_2.id,
                "product_uom": cls.product_2.uom_id.id,
                "product_uom_qty": 25.0,
                "price_unit": 400.0,
            }
        )
        cls.order_line_max_2 = cls.sale_order_line_obj.create(
            {
                "order_id": cls.sale_order_max_1.id,
                "product_id": cls.product_3.id,
                "product_uom": cls.product_3.uom_id.id,
                "product_uom_qty": 25.0,
                "price_unit": 500.0,
            }
        )

        # Create calculation - Compute Sales Order Discount (SALE_DISCOUNT)
        cls.calculation_discount = cls.calculation_obj.create(
            {
                "name": "Compute Sales Order Discount",
                "reference": "SALE_DISCOUNT",
                "model_id": partner_model.id,
            }
        )
        cls.calculation_discount_block = cls.calculation_block_obj.create(
            {
                "name": "Apply Sales Order Discount",
                "reference": "APPLY_DISCOUNT",
                "expression": """discount_multiplier = (100-DISCOUNT_PERCENT)/100\n"""
                """RESULT["final_price"] = SALE_TOTAL * discount_multiplier""",
            }
        )
        cls.calculation_discount_line = cls.calculation_line_obj.create(
            {
                "calculation_id": cls.calculation_discount.id,
                "block_id": cls.calculation_discount_block.id,
                "condition": 'SALE_TOTAL > 10000 and CITY_NAME.upper() == "NEW YORK"',
            }
        )
        cls.calc_discount_variable_1 = cls.calculation_variable_obj.create(
            {
                "name": "CITY_NAME",
            }
        )
        cls.calc_discount_variable_2 = cls.calculation_variable_obj.create(
            {
                "name": "SALE_TOTAL",
            }
        )
        cls.calc_discount_variable_3 = cls.calculation_variable_obj.create(
            {
                "name": "DISCOUNT_PERCENT",
            }
        )
        cls.calculation_discount_variable_line_1 = (
            cls.calculation_variable_line_obj.create(
                {
                    "variable_id": cls.calc_discount_variable_1.id,
                    "value": "record.city",
                    "calculation_id": cls.calculation_discount.id,
                }
            )
        )
        cls.calculation_discount_variable_line_2 = (
            cls.calculation_variable_line_obj.create(
                {
                    "variable_id": cls.calc_discount_variable_2.id,
                    "value": """sum(order.amount_total """
                    """for order in record.sale_order_ids)""",
                    "calculation_id": cls.calculation_discount.id,
                }
            )
        )
        cls.calculation_discount_variable_line_3 = (
            cls.calculation_variable_line_obj.create(
                {
                    "variable_id": cls.calc_discount_variable_3.id,
                    "value": "10",
                    "calculation_id": cls.calculation_discount.id,
                }
            )
        )

        # Create calculation - Partner Loyalty (PARTNER_LOYALTY)
        cls.calculation_loyalty = cls.calculation_obj.create(
            {
                "name": "Partner Loyalty",
                "reference": "PARTNER_LOYALTY",
                "model_id": partner_model.id,
            }
        )
        cls.calculation_loyalty_block_1 = cls.calculation_block_obj.create(
            {
                "name": "Partner Loyalty Block 1",
                "reference": "COMPOSE_LOYALTY_MESSAGE",
                "expression": """RESULT["loyalty_message"] = """
                """f'Such Much {TAX_NUMBER} for {PHONE}'""",
            }
        )
        cls.calculation_loyalty_line_1 = cls.calculation_line_obj.create(
            {
                "calculation_id": cls.calculation_loyalty.id,
                "block_id": cls.calculation_loyalty_block_1.id,
            }
        )
        cls.calculation_loyalty_block_2 = cls.calculation_block_obj.create(
            {
                "name": "Partner Loyalty Block 2",
                "reference": "COMPUTE_POINTS",
                "expression": """message = RESULT["loyalty_message"]  """
                """# this was initialized in the previous block\n"""
                """if message:\n\tRESULT["loyalty_points"] = len(message) * 12\n"""
                """RESULT["loyalty_message"] = "WOW! " + RESULT["loyalty_message"]""",
            }
        )
        cls.calculation_loyalty_line_2 = cls.calculation_line_obj.create(
            {
                "calculation_id": cls.calculation_loyalty.id,
                "block_id": cls.calculation_loyalty_block_2.id,
                "condition": "MOBILE == False",
            }
        )
        cls.calc_loyalty_variable_1 = cls.calculation_variable_obj.create(
            {
                "name": "TAX_NUMBER",
            }
        )
        cls.calc_loyalty_variable_2 = cls.calculation_variable_obj.create(
            {
                "name": "PHONE",
            }
        )
        cls.calc_loyalty_variable_3 = cls.calculation_variable_obj.create(
            {
                "name": "MOBILE",
            }
        )
        cls.calculation_loyalty_variable_line_1 = (
            cls.calculation_variable_line_obj.create(
                {
                    "variable_id": cls.calc_loyalty_variable_1.id,
                    "value": "record.vat",
                    "calculation_id": cls.calculation_loyalty.id,
                }
            )
        )
        cls.calculation_loyalty_variable_line_2 = (
            cls.calculation_variable_line_obj.create(
                {
                    "variable_id": cls.calc_loyalty_variable_2.id,
                    "value": "record.phone",
                    "calculation_id": cls.calculation_loyalty.id,
                }
            )
        )
        cls.calculation_loyalty_variable_line_3 = (
            cls.calculation_variable_line_obj.create(
                {
                    "variable_id": cls.calc_loyalty_variable_3.id,
                    "value": "record.mobile",
                    "calculation_id": cls.calculation_loyalty.id,
                }
            )
        )

    def test_base_calculation(self):
        """Test Calculation Method"""
        records_to_process = (
            self.res_partner_bob + self.res_partner_mike + self.res_partner_max
        )
        initial_values = {
            "DISCOUNT_PERCENT": 25,
            "DISCOUNT_POLICY": "maximum_discount",
        }
        reference = "SALE_DISCOUNT"

        # Perform Calculation
        result = self.calculation_obj.calculate(
            reference, records_to_process, **initial_values
        )
        final_prices = set()

        # Check if result is a list
        self.assertIsInstance(result, list)

        # Check if each element in the result is a list
        for record_dict in result:
            # Check if each element in the list is a dictionary
            self.assertIsInstance(record_dict, dict)
            # Check if each record_dict contains the 'final_price' key
            self.assertIn("final_price", record_dict)
            final_prices.add(record_dict["final_price"])

        # Check if 'final_price' is different for each dictionary
        self.assertGreater(
            len(final_prices), 1, "Final prices should be different for each dictionary"
        )

    def test_multi_calculation_blocks(self):
        """Test Multi Calculation Blocks"""
        records_to_process = (
            self.res_partner_bob + self.res_partner_mike + self.res_partner_max
        )
        initial_values = {}
        reference = "PARTNER_LOYALTY"

        # Perform Calculation
        result = self.calculation_obj.calculate(
            reference, records_to_process, **initial_values
        )
        loyalty_messages = set()
        loyalty_points = set()

        # Check if result is a list
        self.assertIsInstance(result, list)

        # Check if each element in the result is a list
        for record_dict in result:
            # Check if each element in the list is a dictionary
            self.assertIsInstance(record_dict, dict)
            # Check if each record_dict contains the 'loyalty_message' key
            self.assertIn("loyalty_message", record_dict)
            loyalty_messages.add(record_dict["loyalty_message"])
            # Check if each record_dict contains the 'loyalty_points' key
            self.assertIn("loyalty_points", record_dict)
            loyalty_points.add(record_dict["loyalty_points"])

        # Check if 'loyalty_message' is different for each dictionary
        self.assertGreater(
            len(loyalty_messages),
            1,
            "Loyalty messages should be different for each dictionary",
        )
        # Check if 'loyalty_points' is different for each dictionary
        self.assertGreater(
            len(loyalty_points),
            1,
            "Loyalty points should be different for each dictionary",
        )
