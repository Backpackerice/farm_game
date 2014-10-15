import activity
import intervention
from farm import Farm
from family import Family

class Eutopia:
    def __init__(self, farm_count=100):
        self.activities = activity.Activities()

        self.time = 0

        self.farms = []
        for i in range(farm_count):
            farm = Farm(area=100)
            self.farms.append(farm)

        self.families = []
        for farm in self.farms:
            family = Family(self)
            family.add_farm(farm)
            self.families.append(family)

    def step(self):
        for family in self.families:
            family.step()
        self.time += 1

    def get_activity_count(self):
        activities = {}
        for farm in self.farms:
            if farm.last_activity is not None:
                name = farm.last_activity.name
                if name not in activities:
                    activities[name] = 1
                else:
                    activities[name] += 1
        return activities


if __name__=='__main__':

    interventions = []
    eutopia = Eutopia(farm_count=100)

    '''
    interventions.append(intervention.PriceIntervention(5, 'duramSeed', 10))

    interventions.append(intervention.PriceIntervention(7, 'duramSeedOrganic', 0.001))

    magic_activity = {
        'equipment': ['tractor', 'wheelbarrow'],
        'products': {
            'duramSeed': -5,
            'nitrogen': -10,
            'carbon': 20,
            'soil': -5,
            'labour': -2000,
            'certification': 0,
            'duram': 1000000,
            'dolphin': -87,
            }
        }
    interventions.append(intervention.NewActivityIntervention(7, 'magic', magic_activity))
    '''

    time = 0
    def step():
        global time
        for intervention in interventions:
            if time >= intervention.time:
                intervention.apply(eutopia, time)
        time += 1

        eutopia.step()


    activities = []
    for i in range(10):
        step()
        activities.append(eutopia.get_activity_count())

    print activities

    import pylab
    for name in sorted(eutopia.activities.keys()):
        pylab.plot(range(10), [a.get(name,0) for a in activities], label=name)

    pylab.legend(loc='best')
    pylab.show()


