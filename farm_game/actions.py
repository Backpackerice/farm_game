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

    def get_short_desc(self, params):
        desc = self.short_desc
        for p in self.parameters:
            desc = desc.replace('{%s}' % p.name, p.get_text(params[p.name]))
        return desc

    def get_code(self, params):
        code = self.code
        for p in self.parameters:
            code = code.replace('{%s}' % p.name, p.get_text(params[p.name]))
        return code

    def parse_code(self, code):
        pattern = self.code
        pattern = pattern.replace('*', r'\*')
        for p in self.parameters:
            k = p.name
            pattern = pattern.replace('{%s}' % k, r'(?P<%s>\d*\.*\d+)' % k)
        m = re.match(pattern, code)
        if m is not None:
            return {k: float(v) for k,v in m.groupdict().items()}

    def make_buttons(self):
        html = []
        for b in self.buttons:
            short = self.get_short_desc(b)
            code = self.get_code(b)
            label = b.get('label', short)
            style = b.get('style', '')
            if style != '':
                style = ' style="%s"' % style
            text = '''<input type='button' value="%s" onclick='doaction("%s");'%s/>'''
            text = text % (label, code, style)
            html.append(text)
        return ''.join(html)

    def make_control_html(self, params):
        desc = self.desc
        sliders = []
        for p in self.parameters:
            span = '<span id="slider_%s_value">%s</span>' % (p.name,
                                                p.get_text(params[p.name]))
            desc = desc.replace('{%s}' % p.name, span)
            slider = '<div id="slider_%s"></div>' % p.name
            sliders.append(slider)
        return '%s %s' % (desc, ''.join(sliders))

    def make_control_code(self, params):
        replace = ''
        for p in self.parameters:
            replace += "action=action.replace('{%s}', d3.select('#slider_%s_value').text()); " % (p.name, p.name)
        code = []
        for p in self.parameters:
            code.append('''
function slide_%(name)s_func(event, value) {
        d3.select('#slider_%(name)s_value').text(value.toFixed(%(decimals)d));
}

function slide_%(name)s_funcend(event, value) {
    action = "%(code)s";
    %(replace)s
    doaction(action, true);
}

d3.select('#slider_%(name)s').call(d3.slider()
                             .min(%(min)g)
                             .axis(true)
                             .max(%(max)g)
                             .value(%(value)g)
                             .on("slide", slide_%(name)s_func)
                             .on("slideend", slide_%(name)s_funcend));
''' % dict(name=p.name, min=p.min, max=p.max, value=params[p.name],
           decimals=p.decimals, code=self.code, replace=replace))

        return ''.join(code)







class Parameter(object):
    def __init__(self, name, min, max, decimals):
        self.name = name
        self.min = min
        self.max = max
        self.decimals = decimals
    def get_text(self, value):
        return '%g' % round(value, self.decimals)


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

    def make_buttons(self):
        html = []
        for a in self.actions:
            html.append(a.make_buttons())
        return ' '.join(html)

    def make_actions(self):

        # INTERVENTIONS
        a = Action(self)
        a.desc = '''Make no policy changes.'''
        a.code = 'none'
        a.short_desc = 'Nothing New'
        #a.add_button(label='Do Nothing')

        a = Action(self)
        a.add_parameter('p_conv', min=0, max=2.0, decimals=2)
        a.add_parameter('p_org', min=0, max=2.0, decimals=2)
        a.add_parameter('fixed_cost', min=0, max=100000, decimals=0)
        a.desc = '''Slider 1: Premium paid by consumers for local peaches: ${p_conv}/lb.
        Slider 2:  Premium paid by consumers for local organic peaches: ${p_org}/lb.
        Slider 3: One-time public cost for campaign: ${fixed_cost}.'''
        a.code = 'local:{p_conv},{p_org},{fixed_cost}'
        a.short_desc = 'Local: ${p_conv}, ${p_org} | ${fixed_cost}'
        a.add_button(p_conv=0.05, p_org=0.2, fixed_cost=10000,
                label="Marketing 'Local'", style="background:yellow")

        a = Action(self)
        a.add_parameter('price', min=0, max=1.0, decimals=2)
        a.add_parameter('retail', min=0, max=1.0, decimals=2)
        a.add_parameter('yield_inc', min=0.0, max=100.0, decimals=0)
        a.add_parameter('fixed_cost', min=0, max=20000, decimals=0)
        a.desc = '''<strong>Slider 1</strong>: Premium for higher quality and longer life to farmers: <strong>${price}/lb</strong>.
        &nbsp;&nbsp;&nbsp;&nbsp;
        &nbsp;&nbsp;&nbsp;&nbsp;
        <strong>Slider 2:</strong> Premium for higher quality and longer life to retailers: <strong>${retail}/lb.</strong><br/>
        <strong>Slider 3:</strong> Increased yield due to less waste: <strong>{yield_inc}%</strong>
        &nbsp;&nbsp;&nbsp;&nbsp;
        &nbsp;&nbsp;&nbsp;&nbsp;
        <strong>Slider 4:</strong> One-time public cost per farmer: <strong>${fixed_cost}/farm</strong>.'''
        a.code = 'quality:{price},{retail},{yield_inc},{fixed_cost}'
        a.short_desc = 'Qual: ${price}, ${retail}, {yield_inc}% | ${fixed_cost}'
        a.add_button(price=0.05, retail=0.05, fixed_cost=1000, yield_inc=0,
                label="Quality in Shipping", style="background:yellow")

        a = Action(self)
        a.add_parameter('percent', min=0, max=100.0, decimals=0)
        a.desc = '''Create a {percent}% subsidy on certification.'''
        a.code = 'subsidy:certification,{percent}'
        a.short_desc = 'Cert. Subsidy: {percent}%'
        a.add_button(percent=50, label='Certification Subsidy', style="background:yellow")

        # MARKET FORCES/BROADER SYSTEM. PUT ON A DIFFERENT LINE OR COLOUR
        a = Action(self)
        a.add_parameter('price', min=0, max=10.0, decimals=2)
        a.desc = '''Farmer's selling price for grapes, a competing product: ${price}.'''
        a.code = 'price:grapes={price}'
        a.short_desc = 'Compete. Price: ${price}'
        a.add_button(price=5, label="Competitor's Price")

        a = Action(self)
        a.add_parameter('wage', min=0, max=20.0, decimals=2)
        a.desc = '''Cost of labour: ${wage}/hr.'''
        a.code = 'price:labour={wage}'
        a.short_desc = 'Min. Wage = ${wage}'
        a.add_button(wage=11.00, label='Minimum Wage')

        # # ADD A BUTTON FOR PRICE ON CARBON
        # a = Action(self)
        # a.add_parameter('price', min=0, max=20.0, decimals=2)
        # a.desc = '''Cost of carbon: ${price}/hr.'''
        # a.code = 'price:RedHaven={price}'
        # a.short_desc = 'Cost. Carbon = ${price}'
        # a.add_button(price=5, label='Price on Carbon')


        # a = Action(self)
        # a.add_parameter('price', min=0.01, max=100.0, decimals=2)
        # a.desc = '''Price for organic Baby Gold peaches: ${price}'''
        # a.code = 'price:peachesOrganicBabyGold={price}'
        # a.short_desc = 'Org.BabyGold={price}'
        # a.add_button(price=65)

        # a = Action(self)
        # a.add_parameter('price', min=0.01, max=100.0, decimals=2)
        # a.desc = '''Price for non-organic Baby Gold peaches: ${price}'''
        # a.code = 'price:peachesBabyGold={price}'
        # a.short_desc = 'BabyGold={price}'
        # a.add_button(price=55)

        # a = Action(self)
        # a.add_parameter('price', min=0.01, max=100.0, decimals=2)
        # a.desc = '''Price for organic Red Haven peaches: ${price}'''
        # a.code = 'price:peachesOrganicRedhaven={price}'
        # a.short_desc = 'Org.RedHaven={price}'
        # a.add_button(price=65)

        # a = Action(self)
        # a.add_parameter('price', min=0.01, max=100.0, decimals=2)
        # a.desc = '''Price for non-organic Red Haven peaches: ${price}'''
        # a.code = 'price:peachesRedhaven={price}'
        # a.short_desc = 'RedHaven={price}'
        # a.add_button(price=55)

        # a = Action(self)
        # a.add_parameter('price', min=0.01, max=100.0, decimals=2)
        # a.desc = '''Price for grapes: ${price}'''
        # a.code = 'price:grapes={price}'
        # a.short_desc = 'grapes={price}'
        # a.add_button(price=15)

        # a = Action(self)
        # a.add_parameter('price', min=0.01, max=100.0, decimals=2)
        # a.desc = '''Cost of labour: ${price}'''
        # a.code = 'price:labour={price}'
        # a.short_desc = 'labour={price}'
        # a.add_button(price=5)

        # a = Action(self)
        # a.add_parameter('price', min=0.01, max=10.0, decimals=2)
        # a.desc = '''Cost of Certification: ${price}'''
        # a.code = 'price:certification={price}'
        # a.short_desc = 'certification={price}'
        # a.add_button(price=1)





if __name__ == '__main__':
    actions = Actions()
    a, p = actions.find_action('price:peachesOrganicBabyGold=20.5')
    print a.get_short_desc(p)
    a, p = actions.find_action('price:peachesOrganicBabyGold*2')
    print a.get_short_desc(p)
    a, p = actions.find_action('nothing')
    print a.get_short_desc(p)


