To trigger a calculation you need to call the "calculate(reference, records, **kwargs)" function of the "base.calculation" model and pass a Calculation reference, records and initial variable values as kwargs.

Example:

records_to_process = self.env["res.partner"].browse([1,3,4])
initial_values = {"DISCOUNT_PERCENT": 25, "DISCOUNT_POLICY": "maximum_discount"}
result = selv.env["base.calculation").calculate("SALES_DISCOUNT", records_to_process, **initial_values)
This call will evaluate the "Compute Sales Order Discount"(ref="SALES_DISCOUNT") Calculation and assign the result to the "result" value.