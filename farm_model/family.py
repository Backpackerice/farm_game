class Family:
    def __init__(self, eutopia):
        self.eutopia = eutopia
        self.farms = []
        self.bank_balance = 1000000.00
        self.equipment = []
        self.preferences = {'money': 1}
        self.future_discounting = 0.9
        self.future_steps = 10

    def add_farm(self, farm):
        self.farms.append(farm)
        farm.family = self

    def make_planting_decision(self, activities, farm):
        best = None
        for activity in activities:
            total = 0
            future_farm = farm.copy()
            future_farm.last_activity = activity

            scale = 1.0
            for i in range(self.future_steps):
                future_farm.update()

                for pref, weight in self.preferences.items():
                    total += activity.get_product(pref, future_farm) * weight
                scale *= self.future_discounting

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
            farm.update()

