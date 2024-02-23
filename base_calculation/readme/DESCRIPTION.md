This is a technical module that implements pre-defined Calculations that consist of Calculation Blocks used to compute different values based on various Odoo models.
It works similar to Automated Actions however the main difference is that it returns result as a set of value that should be evaluated further in other Odoo modules.

Calculation 

Each calculation consist of Calculation Lines which defines what will happen when calculation process will reach it.

Each Calculation Line has the following settings:

- Sequence. Positional order of the block in the calculation chain. Calculation blocks are processed in order from the lowest to the highest sequence number.
- Condition. Python expression that must be complied to run this line.
- Calculation Block that will be evaluated.