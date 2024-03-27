There are different cases when you need to calculate some values based on data that is located in different models.
These values computation flow depends on different parameters and user should be able to configure them without having to have too much technical knowledge. 

For example you need to calculate a car insurance premiums base on the following information:

- Driver's age. This data is located in the "Partners" model.
- Car engine displacement and power. This data is located in the "Cars" model.
- Region where an insurance is issued. This data is located in the "Insurance Offices" model.
- Current promo actions. This data is stored in the "Promos" model.

Here are some formula examples:

Formula A

If Driver's age is Between 18 and 21 AND Car BHP<=200HP then:
Premium = BasePremium + (BasePremium * (1 + (Driver's Age -18)/10)) ) + AgeSurcharge + CarBHP* RegionalCoefficient

Formula B

If Driver's age is  More than 21  then:

Premium = BasePremium*CurrentPromoDiscount + CarBHP*RegionalCoefficient*CurrentPromoDiscount

However those formulas have a tendency to frequent changes and there should be an easy way to compose and update them without any coding and too much technical knowledge.