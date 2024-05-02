# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
{
    "name": "Base Calculation Code Builder",
    "summary": "Build Calculation code directly from UI",
    "version": "16.0.1.0.0",
    "category": "Extra Tools",
    "website": "https://cetmix.com",
    "author": "Cetmix",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "images": ["static/description/banner.png"],
    "depends": ["cetmix_calculation"],
    "data": [
        "security/ir.model.access.csv",
        "views/base_calculation_block_view.xml",
        "views/base_calculation_expression_view.xml",
    ],
}
