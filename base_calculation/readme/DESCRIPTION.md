This is a technical module that implements pre-defined Calculations that consist of Calculation Blocks used to compute different values based on various Odoo models.
It works similar to Automated Actions however the main difference is that it returns result as a set of value that should be evaluated further in other Odoo modules.

Calculation 

Each calculation block has the following settings:

- Sequence. Positional order of the block in the calculation chain. Calculation blocks are processed in order from the lowest to the highest sequence number.
- Condition. A Python expression which describes when the block is involved in the calculation chain.
- Action. A Python expression that performs the evaluations within the block.
