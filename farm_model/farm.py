class Counter:
    def __init__(self):
        self.data = {}
    def update(self, items):
        keys = self.data.keys()
        for k in items:
            self.data[k] = self.data.get(k, 0) + 1
        for k in self.data.keys():
            if k not in items:
                del self.data[k]
    def __getattr__(self, key):
        if not key.startswith('_'):
            return self.data.get(key)
        raise AttributeError


class Farm:
    def __init__(self, eutopia, area):
        self.area = area
        self.last_activity = None
        self.counter = Counter()
        self.eutopia = eutopia

    def update(self):
        self.counter.update(self.last_activity.counters)

    def copy(self):
        f = Farm(self.eutopia, self.area)
        f.last_activity = self.last_activity
        f.counter.data.update(self.counter.data)
        return f
