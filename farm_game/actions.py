import re

class Action(object):
    def __init__(self, actions):
        self.desc = None
        self.code = None
        self.short_desc = None
        self.parameters = []
        actions.actions.append(self)
        self.buttons = []
    def add_parameter(self, name, min, max, decimals):
        self.parameters.append(Parameter(name, min, max, decimals))
    def add_button(self, **kwargs):
        self.buttons.append(dict(**kwargs))

    def parse_code(self, code):
        pattern = self.code
        pattern = pattern.replace('*', r'\*')
        for p in self.parameters:
            k = p.name
            pattern = pattern.replace('{%s}' % k, r'(?P<%s>\d*\.*\d+)' % k)
        m = re.match(pattern, code)
        if m is not None:
            return {k: float(v) for k,v in m.groupdict().items()}


class Parameter(object):
    def __init__(self, name, min, max, decimals):
        self.name = name
        self.min = min
        self.max = max
        self.decimals = decimals


class Actions(object):
    def __init__(self):
        self.actions = []
        self.make_actions()

    def find_action(self, code):
        for a in self.actions:
            result = a.parse_code(code)
            if result is not None:
                return a, result
        return None

    def make_actions(self):
        a = Action(self)
        a.add_parameter('price', min=0.01, max=100.0, decimals=2)
        a.desc = '''Farmers sell organic peaches at ${price} per ton.'''
        a.code = 'price:peachesOrganicBabyGold={price}'
        a.short_desc = 'OrganicBG={price}'
        a.add_button(price=20)
        a.add_button(price=50)
        a.add_button(price=100)

        a = Action(self)
        a.add_parameter('scale', min=0.1, max=10.0, decimals=2)
        a.desc = '''Farmers sell organic peaches at {scale} times old price.'''
        a.code = 'price:peachesOrganicBabyGold*{scale}'
        a.short_desc = 'OrganicBG*{scale}'
        a.add_button(scale=0.5)
        a.add_button(scale=2)



if __name__ == '__main__':
    actions = Actions()
    print actions.find_action('price:peachesOrganicBabyGold=20.5')
    print actions.find_action('price:peachesOrganicBabyGold*2')


