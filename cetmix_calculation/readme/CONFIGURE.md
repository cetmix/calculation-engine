Activate the "Developer Mode".

To configure a Calculation

Go to "Settings/Technical/Calculations/Calculation" and create a new Calculation:

`Name`. Readable name of the Calculation.

`Reference`. This is a unique reference of the Calculation that will be used in expressions. Must contain CAPITAL_LETTERS_NUMBERS_EG_1_AND_UNDERSCORES_ONLY

`Model`. Base model used by the Calculation. Same as "model" keyword in server actions.

`Variables`. List of pre-defined variables that will be populated to the Calculation Blocks. Python expressions can be used same as in server actions. 
Example (model = res.partner)

CITY_NAME = record.city_id.name
SALE_TOTAL = record.sale_order_ids.amount_total
DISCOUNT_PERCENT = 10

`Blocks`. List of calculation blocks and conditions to be met to trigger them.
Example (order, block, condition)
10, "Apply Discount", SALE_TOTAL > 10000 and CITY_NAME.upper() == "NEW YORK"



To configure a Calculation Block

Go to "Settings/Technical/Calculations/Calculation Blocks" and create a new Calculation Block:

`Name`. Readable name of the Calculation Block.

`Reference`. This is a unique reference of the Calculation that will be used in expressions. Must contain CAPITAL_LETTERS_NUMBERS_EG_1_AND_UNDERSCORES_ONLY

`Expression`. Python expression. Must assign a value to the built-in RESULT variable.
Example:

discount_multiplier = (100-DISCOUNT_PERCENT)/100
RESULT["final_price"] = SALE_TOTAL * discount_multiplier
Built-in variables

Following global and built-in variables are accessible from any expression:

`RESULT`: dictionary with values. Holds the current result of the Calculation process as it is available at the moment of the expression evaluation.
You can also get the RESULT as it is available at the the particular Calculation Block output. Those values are accessible using CALCULATUION_BLOCK_REFERENCE.RESULT

You must take care of which values are being stored there. In case of any value incompatibility and exception will be raised.


Calculation Block references are accessible globally within the Calculation Block

You can also define global variables. This variables are not connected to any specific calculation and are shared between all of them.
They can be used as default parameters in case a value is not defined on the calculation level.
Important! if you are using model properties in global variable values (eg record.partner_id.name​) you must ensure that the model you are using such variables in has those properties.
Global variable values are overridden by calculation defined values and by values propagated from code.
