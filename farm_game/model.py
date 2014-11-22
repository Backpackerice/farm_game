from collections import OrderedDict
import numpy as np
import farm_model

class Model:
    farm_width = 7
    farm_height = 7
    farm_count = farm_width * farm_height
    products = [
                'peachesRedhaven',
                'peachesBabyGold',
                'peachesOrganicRedhaven',
                'peachesOrganicBabyGold',
                'grapes',
                'labour',
                'carbon',
                'nitrogen',
                'soil',
                'biodiversity',
                'govt_cost',
                'retail_profit',
               ]



    def __init__(self, seed=None):
        self.rng = np.random.RandomState(seed=seed)
        self.model = farm_model.eutopia.Eutopia(farm_count=Model.farm_count,
                                                rng=self.rng)

        self.steps = -10    # starting time step
        self.interventions = []
        self.data = {}
        self.init_data()

    def step(self):
        self.steps += 1
        for interv in self.interventions:
            if self.steps > interv.time:
                interv.apply(self.model, self.steps)

        self.model.step()

        self.update_data()

    def init_data(self):
        for name in self.model.activities.keys():
            self.data['act_' + name] = []
        self.data['total_bankbalance'] = []
        self.data['total_income'] = []
        for p in self.products:
            self.data['prod_' + p] = []

    def update_data(self):
        if self.steps >= 0:

            acts = self.model.get_activity_count()

            for name in self.model.activities.keys():
                self.data['act_' + name].append(acts.get(name, 0) * 100.0 /
                                                float(self.farm_count))
            self.data['total_bankbalance'].append(self.get_total_balance())
            self.data['total_income'].append(self.get_total_income())
            for p in self.products:
                self.data['prod_' + p].append(self.get_product(p))

    def get_total_balance(self):
        return sum([f.bank_balance for f in self.model.families])
    def get_total_income(self):
        return sum([f.income for f in self.model.families])
    def get_product(self, product):
        v = sum([f.last_activity.get_product(product, f)
                    for f in self.model.farms])
        if product == 'govt_cost':
            v += self.model.govt_cost
            self.model.govt_cost = 0
        return v

    def get_grid(self):
        grid = []
        width = self.farm_width
        height = self.farm_height
        for j in range(height):
            for i in range(width):
                a = self.model.farms[j*width + i].last_activity
                color = a.color
                info = 'activity: %s' % a.name
                item = dict(type='farm', x=i, y=j, color=color, info=info)
                grid.append(item)
        return grid

    def get_data(self):
        self.data['grid'] = self.get_grid()
        return self.data


def memoize(f):
    """ Memoization decorator for functions taking one or more arguments. """
    class memodict(dict):
        def __init__(self, f):
            self.f = f
        def __call__(self, *args):
            return self[args]
        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret
    return memodict(f)

def clear_cache():
    model_cache.clear()
    run.clear()  # clear the memoized cache too


model_cache = {}
import copy

def find_cached_model(seed, actions):
    for step in reversed(range(len(actions)+1)):
        result = model_cache.get((seed, tuple(actions[:step])), None)
        if result is not None:
            step, model = result
            print '  found', step
            return step, copy.deepcopy(model)
    model = Model(seed=seed)
    while model.steps < 0 :
        model.step()
    model_cache[(seed, ())] = -1, copy.deepcopy(model)
    return -1, model

@memoize
def run(seed, *actions):
    step, model = find_cached_model(seed, actions)
    for i, act in enumerate(actions):
        if i > step:
            for action in act.split(';'):
                # add intervention
                interv = None

                if action == 'init':
                    pass
                elif action == 'none':
                    pass
                elif action.startswith('subsidy:'):
                    product, percent = action[8:].split(',')
                    percent=float(percent) * 20
                    interv = farm_model.intervention.SubsidyIntervention(i, product, percent)
                elif action.startswith('quality:'):
                    price, retail, yield_inc, fixed_cost = action[8:].split(',')
                    price = float(price) * 10
                    retail = float(retail) * 10
                    yield_inc = float(yield_inc) / 100.0
                    fixed_cost = float(fixed_cost) * 49
                    interv = farm_model.intervention.QualityAndShippingIntervention(
                            i, price, retail, yield_inc, fixed_cost)
                elif action.startswith('sd:'):
                    product, p_max, p_min, slope = action[3:].split(',')
                    scale_price = 10.0;
                    scale_quantity = 1000.0;
                    interv = farm_model.intervention.SupplyDemandIntervention(
                            i, product, p_max=float(p_max) * scale_price,
                                        p_min=float(p_min) * scale_price,
                                        slope=float(slope) / scale_quantity)
                elif action.startswith('local:'):
                    price_conv, price_org, fixed_cost = action[6:].split(',')
                    interv = farm_model.intervention.LocalMarketIntervention(
                            i, float(price_conv) * 10, float(price_org) * 10,
                            float(fixed_cost))
                elif action.startswith('price:'):
                    if '*' in action[6:]:
                        product, value = action[6:].split('*')
                        value = float(value)
                        interv = farm_model.intervention.PriceScaleIntervention(i, product, value)
                    elif '=' in action[6:]:
                        product, value = action[6:].split('=')
                        value = float(value)
                        if product == 'grapes':
                            value = value * 5
                        if product == 'labour':
                            value = value * 5.0 / 11.0
                        interv = farm_model.intervention.PriceIntervention(i, product, value)
                else:
                    print 'WARNING: Unknown intervention', action

                if interv is not None:
                    model.interventions.append(interv)


            model.step()

            model_cache[(seed, tuple(actions[:(i+1)]))] = (i, copy.deepcopy(model))



    return model.get_data()


if __name__ == '__main__':

    #data = run(1, 'init', 'none', 'none', 'price:peachesOrganicBabyGold*20', 'none', 'none', 'none')
    #data = run(2, 'init', 'none', 'subsidy:certification,100', 'none', 'none', 'none', 'none')
    #data = run(2, 'init', 'none', 'none', 'none', 'none', 'none', 'none')
    #data = run(2, 'init', 'none', 'none', 'quality:20,20,10000', 'none', 'none', 'none')
    #data = run(3, 'init;sd:peachesRedhaven,100,0,0')#, 'none', 'none')
    #data = run(2, 'init;sd:peachesRedhaven,100,0,0')#, 'none', 'none')
    data = run(2, 'init', 'none', 'sd:peachesRedhaven,100,0,0', 'none', 'none')
    data = run(3, 'init', 'none', 'sd:peachesRedhaven,100,0,0', 'none', 'none')

    print data

    import pylab
    for k, v in data.items():
        if k.startswith('act_'):
            pylab.plot(v, label=k[4:], linewidth=3)
    pylab.legend(loc='best')
    pylab.show()


