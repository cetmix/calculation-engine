# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
{
    "name": "Cetmix calculation pricelist",
    "summary": "This module implements connection between cetmix_calculation"
    " module and Odoo pricelists",
    "version": "16.0.1.0.0",
    "category": "Extra Tools",
    "website": "https://cetmix.com",
    "author": "Cetmix",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "images": ["static/description/banner.png"],
    "depends": ["cetmix_calculation", "product", "sale_management"],
    "data": ["views/product_pricelist_item_view.xml"],
}
