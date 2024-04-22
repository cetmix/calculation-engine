# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
from odoo.addons.base.tests.common import BaseCommon


class TestBaseCalculation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_obj = cls.env["res.partner"]
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
        cls.calculation_loyalty_block_3 = cls.calculation_block_obj.create(
            {
                "name": "Partner Loyalty Block 3",
                "reference": "PARTNER_LOYALTY_BLOCK_3",
                "expression": """message = """
                """COMPOSE_LOYALTY_MESSAGE.RESULT["loyalty_message"]\n"""
                """if message:\n\tRESULT["compose_loyalty_message"] = message\n""",
            }
        )
        cls.calculation_loyalty_line_3 = cls.calculation_line_obj.create(
            {
                "calculation_id": cls.calculation_loyalty.id,
                "block_id": cls.calculation_loyalty_block_3.id,
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
                }
            )
        )
        cls.calculation_loyalty_variable_line_2 = (
            cls.calculation_variable_line_obj.create(
                {
                    "variable_id": cls.calc_loyalty_variable_2.id,
                    "value": "record.phone",
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
        initial_values = {}
        reference = "PARTNER_LOYALTY"
        # Get calculation by reference
        my_calculation = self.env["base.calculation"].get_by_reference(reference)

        # Perform Calculation
        result = my_calculation.calculate(records_to_process, **initial_values)

        loyalty_messages = set()
        loyalty_points = set()

        # Check if result is a dict
        self.assertIsInstance(result, dict)

        # Check if each item in the result is a dict
        for record_id, calculation_result in result.items():
            # Check if record_id is partner id
            partner = self.partner_obj.browse([int(record_id)])
            self.assertEqual(partner.id, int(record_id), "Partner not found")

            # Check if each record_dict contains the 'loyalty_message' key
            self.assertIn("loyalty_message", calculation_result)
            loyalty_messages.add(calculation_result["loyalty_message"])

            # Check if each record_dict contains the 'loyalty_points' key
            self.assertIn("loyalty_points", calculation_result)
            loyalty_points.add(calculation_result["loyalty_points"])

            # Check if each record_dict contains the 'compose_loyalty_message' key
            self.assertIn("compose_loyalty_message", calculation_result)

            # Check if compose_loyalty_message is different than loyalty_message
            self.assertNotEqual(
                calculation_result["compose_loyalty_message"],
                calculation_result["loyalty_message"],
            )

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

    def test_normalize_variable_name(self):
        """Test Normalize Variable Name"""
        test_cases = [
            ("normalVariable", "normalvariable"),
            ("NORMAL_VAR@", "normal_var"),
            ("NORMAL_VAR", "NORMAL_VAR"),
            ("VariableWithCAPS", "variablewithcaps"),
            ("123startWithNumber", "var_123startwithnumber"),
            ("special!@#$", "special"),
            ("with spaces", "with_spaces"),
            ("__leadingUnderscores", "leadingunderscores"),
            ("trailingUnderscores__", "trailingunderscores"),
            ("class", "var_class"),
            ("@@@@@%%", "var_default"),
            ("normal variable @@@@@%%", "normal_variable"),
        ]

        # Test each case
        for original_name, expected_name in test_cases:
            variable = self.calculation_variable_obj.create({"name": original_name})
            self.assertEqual(
                variable.name,
                expected_name,
                f"Failed normalization: Expected {expected_name}, got {variable.name}.",
            )
