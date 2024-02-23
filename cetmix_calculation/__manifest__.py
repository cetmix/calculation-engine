# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
{
    "name": "Odoo Calculation Engine",
    "summary": "Calculate values using various model data",
    "version": "16.0.1.0.0",
    "category": "Extra Tools",
    "website": "https://cetmix.com",
    "author": "Cetmix",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "images": ["static/description/banner.png"],
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/base_calculation_test_view.xml",
        "views/base_calculation_view.xml",
        "views/base_calculation_variable_view.xml",
        "views/base_calculation_block_view.xml",
        "views/base_calculation_variable_line_view.xml",
    ],
}
