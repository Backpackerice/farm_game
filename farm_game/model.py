from collections import OrderedDict
import numpy as np
import farm_model

class Model:
    farm_width = 14
    farm_height = 14
    farm_count = farm_width * farm_height

    def __init__(self, seed=None):
        self.rng = np.random.RandomState(seed=seed)
        self.model = farm_model.eutopia.Eutopia(farm_count=Model.farm_count)

        self.steps = -2    # starting time step
        self.interventions = []
        self.data = {}
        self.init_data()

    def step(self):
        self.steps += 1
        for interv in self.interventions:
            if self.steps > interv.time:
                interv.apply(self, self.steps)

        self.model.step()

        self.update_data()

    def init_data(self):
        for name in self.model.activities.keys():
            self.data['act_' + name] = []

    def update_data(self):
        if self.steps >= 0:

            acts = self.model.get_activity_count()

            for name in self.model.activities.keys():
                self.data['act_' + name].append(acts.get(name, 0) * 100.0 /
                                                float(self.farm_count))

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
            return step, copy.deepcopy(model)
    model = Model(seed=seed)
    while model.steps < 0 :
        model.step()
    model_cache[(seed, ())] = -1, copy.deepcopy(model)
    return -1, model

@memoize
def run(seed, *actions):
    step, model = find_cached_model(seed, actions)
    for i, action in enumerate(actions):
        if i > step:
            # add intervention

            model.step()

            model_cache[(seed, tuple(actions[:(i+1)]))] = (i, copy.deepcopy(model))



    return model.get_data()


if __name__ == '__main__':
    print run(1, 'init')

