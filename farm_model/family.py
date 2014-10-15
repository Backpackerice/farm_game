class Family:
    def __init__(self, eutopia):
        self.eutopia = eutopia
        self.farms = []
        self.bank_balance = 1000000.00
        self.equipment = []
        self.preferences = {'money': 1}

    def add_farm(self, farm):
        self.farms.append(farm)
        farm.family = self

    def make_planting_decision(self, activities, farm):
        best = None
        for activity in activities:
            total = 0
            for pref, weight in self.preferences.items():
                total += activity.get_product(pref, farm) * weight
                # TODO: improve choice algorithm
                #    - maybe by allowing different sensitivities to risk
                #      on different income dimensions

            if best is None or total > best_total:
                best = activity
                best_total = total

        return best


    def step(self):
        for farm in self.farms:
            activity = self.make_planting_decision(
                self.eutopia.activities.activities, farm)

            money = activity.get_product('money', farm)
            self.bank_balance += money

            farm.last_activity = activity

