# TODO: think about fixed costs and non-linear (economies of scale)
# TODO: include equipment

# http://www.vinelandgrowers.com/index.php?p=Our_Fruit#Peaches
# http://eap.mcgill.ca/MagRack/BAH/BAH%202.htm econ of fruit production



activities = {
	 # Fresh, mid August, freestone.
    'Redhaven': {
        'equipment': ['tractor'],
        'times': {
        	'certificationDelayYears': 0,
        	 'harvestStartYear': 7,
        	 'harvestEndYear':	30,
            'harvestStartWeek': 33, 	# mid august for 3 weeks?
            'havestEndWeek': 36,
            'shelfLifeWeeks': 1, 		# weeks from picking
        	},
        'products': {
            'peachesRedhaven': '35 if farm.counter.red_haven > 7 else 0', 		# total tons per km^2/year
            'nitrogen': -10,		# kg per km^2/year
            'carbon': 10,		# tons per km^2/year
            'soil': -0.001,		# inches per km^2/year
            'labour': -200,		# hours per km^2/year
            'certification': 0,
            },
        'color': '#FF0066',
        'counters': ['red_haven'],
        },
    'Redhaven Organic': {
        'equipment': ['tractor'],
        'times': {
        	'certificationDelayYears': 3,
        	 'harvestStartYear': 7,
        	 'harvestEndYear':	30,
            'harvestStartWeek': 33, 	# mid august for 3 weeks?
            'havestEndWeek': 36,
            'shelfLifeWeeks': 1, 		# weeks from picking
        	},
        'products': {
            'peachesOrganicRedhaven': '30 if farm.counter.red_haven > 7 and farm.counter.organic > 3 else 0', 		# total tons per km^2?
            'peachesRedhaven': '30 if farm.counter.red_haven > 7 and farm.counter.organic <= 3 else 0', 		# total tons per km^2?
            'nitrogen': 0,
            'carbon': 2,		# tons per km^2?
            'soil': 0.001,		# inches per km^2?
            'labour': -220,		# hours per km^2/year
            'certification': -10, # $/(km^2 year)
            },
        'color': '#009933',
        'counters': ['red_haven', 'organic'],
        },

	 # Canning, late August, freestone.
    'Baby Gold': {
        'equipment': ['tractor'],
        'times': {
        	'certificationDelayYears': 0,
        	 'harvestStartYear': 7,
        	 'harvestEndYear':	30,
            'harvestStartWeek': 35, 	# late august for 3 weeks?
            'havestEndWeek': 38,
            'shelfLifeWeeks': 1, 		# weeks from picking
        	},
        'products': {
            'peachesBabyGold': '35 if farm.counter.baby_gold > 7 else 0', 		# total tons per km^2/year
            'nitrogen': -10,		# kg per km^2/year
            'carbon': 10,		# tons per km^2/year
            'soil': -0.001,		# inches per km^2/year
            'labour': -200,		# hours per km^2/year
            'certification': 0,
            },
        'color': '#FF9933',
        'counters': ['baby_gold'],
        },
    'Baby Gold Organic': {
        'equipment': ['tractor'],
        'times': {
        	'certificationDelayYears': 3,
        	 'harvestStartYear': 7,
        	 'harvestEndYear':	30,
            'harvestStartWeek': 35, 	# late august for 3 weeks?
            'havestEndWeek': 38,
            'shelfLifeWeeks': 1, 		# weeks from picking
        	},
        'products': {
            'peachesOrganicBabyGold': '30 if farm.counter.baby_gold > 7 and farm.counter.organic > 3 else 0', 		# total tons per km^2?
            'peachesBabyGold': '30 if farm.counter.baby_gold > 7 and farm.counter.organic <= 3 else 0', 		# total tons per km^2?
            'nitrogen': 0,
            'carbon': 2,		# tons per km^2?
            'soil': 0.001,		# inches per km^2?
            'labour': -220,		# hours per km^2/year
            'certification': -10, # $/(km^2 year)
            },
        'color': '#33CC33',
        'counters': ['baby_gold', 'organic'],
        },
	 # Coronation seedless grapes, mid August through to end of September.
    'Coronation Grapes': {
        'equipment': ['tractor'],
        'times': {
        	'certificationDelayYears': 0,
        	 'harvestStartYear': 3,		# check
        	 'harvestEndYear':	30,
            'harvestStartWeek': 35, 	# late august for 3 weeks?
            'havestEndWeek': 38,
            'shelfLifeWeeks': 1, 		# weeks from picking
        	},
        'products': {
            'grapes': 35, 		# total tons per km^2/year
            'nitrogen': -10,		# kg per km^2/year
            'carbon': 10,		# tons per km^2/year
            'soil': -0.001,		# inches per km^2/year
            'labour': -200,		# hours per km^2/year
            'certification': 0,
            },
        'color': '#5C00B8',
        'counters': ['grapes'],
        },
    }

class Normal:
    def __init__(self, mean, sd):
        self.mean = mean
        self.sd = sd
    def value(self, rng):
        return rng.randn()*self.sd + self.mean
    def __mul__(self, scale):
        return Normal(self.mean*scale, self.sd*scale)
    def __add__(self, inc):
        return Normal(self.mean + inc, self.sd)


noise = 40
aggregate_measures = {
    'money': {
        'peachesRedhaven': Normal(55,noise),
        'peachesBabyGold': Normal(55,noise),
        'peachesOrganicRedhaven': Normal(65,noise),
        'peachesOrganicBabyGold': Normal(65,noise),
        'grapes': Normal(15,noise),
        'labour': Normal(5,1),
        'certification': Normal(1,0),
        },
    'govt_cost': {
        'certification': Normal(0,0),
        },
    'retail_profit': {
        'peachesRedhaven': Normal(0,0),
        'peachesBabyGold': Normal(0,0),
        'peachesOrganicRedhaven': Normal(0,0),
        'peachesOrganicBabyGold': Normal(0,0),
        'grapes': Normal(0,0),
        },
    'environment': {
        'carbon': Normal(10,0),
        'nitrogen': Normal(10,10),
        'soil':Normal(10,10),
        'biodiversity':Normal(10,100)
        },
    }



class Activity:
    def __init__(self, name, equipment, products, aggregate_measures, times,
                    color, counters):
        self.name = name
        self.equipment = equipment
        self.products = products
        self.aggregate_measures = aggregate_measures
        self.times = times
        self.color = color
        self.counters = counters

    def get_product(self, key, farm):
        if key in self.products.keys():
            value = self.products[key]
            if isinstance(value, str):
                value = eval(value, dict(farm=farm))
            return value * farm.area
        elif key in self.aggregate_measures.keys():
            total = 0
            for item, distribution in self.aggregate_measures[key].items():
                if item in self.products.keys():
                    weight = distribution.value(farm.eutopia.rng)
                    total += weight*self.get_product(item, farm)
            return total

        return 0

class Activities:
    def __init__(self):
        self.aggregates = dict(aggregate_measures)

        self.activities = []
        for name, data in activities.items():
            self.activities.append(Activity(name, aggregate_measures=self.aggregates, **data))

    def keys(self):
        return [a.name for a in self.activities]

if __name__=='__main__':
    activities = Activities()
