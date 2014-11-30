import activity
import numpy as np

class PriceScaleIntervention:
    def __init__(self, time, product, scale, phase_in_time=0):
        self.time = time
        self.product = product
        self.scale = scale
        self.phase_in_time = phase_in_time
        self.original_value = None

    def apply(self, eutopia, time):
        assert time>=self.time

        money = eutopia.activities.aggregates['money']

        if self.original_value is None:
            self.original_value = money[self.product]

        scale = self.scale
        if self.phase_in_time>0:
            ratio = float(time-self.time)/phase_in_time
            if ratio>1: ratio = 1
            scale = scale*ratio

        money[self.product] = self.original_value*scale

class PriceIntervention:
    def __init__(self, time, product, value):
        self.time = time
        self.product = product
        self.value = value
        self.original_value = None

    def apply(self, eutopia, time):
        assert time>=self.time

        money = eutopia.activities.aggregates['money']

        if self.original_value is None:
            self.original_value = money[self.product]

        scale = self.value / self.original_value.mean

        money[self.product] = self.original_value * scale

class SubsidyIntervention:
    def __init__(self, time, product, percent):
        self.time = time
        self.product = product
        self.percent = percent
        self.original_value = None

    def apply(self, eutopia, time):
        assert time>=self.time

        #if time > self.time + 1: return

        money = eutopia.activities.aggregates['money']
        govt_cost = eutopia.activities.aggregates['govt_cost']

        if self.original_value is None:
            self.original_value = money[self.product]

        scale = (100.0 - self.percent) / 100
        money[self.product] = self.original_value * scale

        govt_cost[self.product] = activity.Normal(
                                   -self.original_value.mean * (1-scale), 0)

class QualityAndShippingIntervention:
    def __init__(self, time, price_increase, retail_increase, yield_increase,
                       fixed_cost):
        self.time = time
        self.price_increase = price_increase
        self.retail_increase = retail_increase
        self.yield_increase = yield_increase
        self.fixed_cost = fixed_cost

    def apply(self, eutopia, time):
        assert time>=self.time

        #if time > self.time + 1: return

        money = eutopia.activities.aggregates['money']
        retail = eutopia.activities.aggregates['retail_profit']

        peaches = ['peachesRedhaven', 'peachesBabyGold',
                   'peachesOrganicRedhaven', 'peachesOrganicBabyGold']

        for peach in peaches:
            money[peach] = money[peach] + self.price_increase
            retail[peach] = retail[peach] + self.retail_increase
            for act in eutopia.activities.activities:
                if peach in act.products:
                    value = act.products[peach]
                    if isinstance(value, (int, float)):
                        value = value * (1 + self.yield_increase)
                    elif isinstance(value, str):
                        value = '(%s) * %g' % (value, 1 + self.yield_increase)
                    else:
                        raise Exception('Cannot handle value %s' % value)
                    act.products[peach] = value

        #for f in eutopia.families:
        #    f.bank_balance -= self.fixed_cost
        #    f.income -= self.fixed_cost

        eutopia.govt_cost += self.fixed_cost

class LocalMarketIntervention:
    def __init__(self, time, conv_increase, organic_increase, fixed_cost):
        self.time = time
        self.conv_increase = conv_increase
        self.organic_increase = organic_increase
        self.fixed_cost = fixed_cost

    def apply(self, eutopia, time):
        assert time>=self.time

        #if time > self.time + 1: return

        money = eutopia.activities.aggregates['money']

        for peach in ['peachesRedhaven', 'peachesBabyGold']:
            money[peach] = money[peach] + self.conv_increase

        for peach in ['peachesOrganicRedhaven', 'peachesOrganicBabyGold']:
            money[peach] = money[peach] + self.organic_increase

        eutopia.govt_cost += self.fixed_cost

class NewActivityIntervention:
    def __init__(self, time, name, activity):
        self.time = time
        self.activity = activity
        self.name = name

    def apply(self, eutopia, time):
        if time == self.time:
            a = activity.Activity(self.name,
                    aggregate_measures=eutopia.activities.aggregates,
                    **self.activity)
            eutopia.activities.activities.append(a)

class SupplyDemandIntervention:
    def __init__(self, time, product, p_max, p_min, slope):
        self.time = time
        self.product = product
        self.p_max = p_max
        self.p_min = p_min
        self.slope = slope
        self.original_value = None

    def apply(self, eutopia, time):
        assert time >= self.time

        money = eutopia.activities.aggregates['money']

        if self.original_value is None:
            self.original_value = money[self.product]

        quantity = 0
        for f in eutopia.farms:
            if f.last_activity is not None:
                quantity += f.last_activity.get_product(self.product, f)

        price = np.maximum(-quantity * 0.001 * self.p_max * self.slope + self.p_max, self.p_min)

        print 'time', time, 'quantity', quantity, 'price', price

        difference = price - self.original_value.mean


        money[self.product] = self.original_value + difference




class ArrayPriceIntervention:
    def __init__(self, time, product, values):
        self.time = time
        self.product = product
        self.values = values
        self.original_value = None

    def apply(self, eutopia, time):
        assert time>=self.time

        money = eutopia.activities.aggregates['money']

        if self.original_value is None:
            self.original_value = money[self.product]

        index = time - self.time - 1
        if index >= len(self.values):
            index = len(self.values) - 1


        value = self.values[index]

        if self.original_value.mean == 0:
            money[self.product] = self.original_value + value
        else:
            scale = value / self.original_value.mean
            money[self.product] = self.original_value * scale






