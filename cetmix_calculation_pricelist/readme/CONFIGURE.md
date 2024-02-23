1. Create a Calculation

- Navigate to *Settings -> Technical -> Calculations -> Calculation* and create a new Calculation.

- Refer to the [Cetmix calculation module documentation](https://github.com/cetmix/calculation-engine/tree/16.0-t3273-base_calculation-new_module/cetmix_calculation) for detailed guidance.

2. Variables Exposed to the Calculation

- *ORDER*: The current quotation.

- *ORDER_LINE*: The current quotation line.

- *CUSTOMER*: The quotation customer.

- *RECIPIENT*: The delivery address (partner) for the quotation.

- *PAYER*: The invoice address (partner) for the quotation.

- *Surcharge*: The percentage amount to be added to the option selected in the pricelist *Based on* field 

3. Enable Advanced Price Rules

- Ensure that Advanced Price Rules are enabled. You can reference the [official documentation](https://www.odoo.com/documentation/16.0/applications/sales/sales/products_prices/prices/pricing.html#pricing-strategy-options).