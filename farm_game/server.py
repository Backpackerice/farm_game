import os.path
import json
import random
import uuid as uuid_package
import time
import copy

import pkgutil
import farm_game

import model
import logging
log = logging.Logging()
import actions
all_actions = actions.Actions()


from collections import OrderedDict

import gbm

actions = OrderedDict()
seeds = {}
names = {}

colormap = {
    'total_income': 'magenta',
    'total_bankbalance': 'magenta',
    'prod_grapes': 'purple',
    'prod_peachesOrganicBabyGold': 'gold',
    'prod_peachesBabyGold': 'yellow',
    'prod_peachesOrganicRedhaven': 'pink',
    'prod_peachesRedhaven': 'red',
    'prod_nitrogen': 'blue',
    'prod_carbon': 'black',
    'prod_soil': 'brown',
    'prod_labour': '#888',
    'prod_biodiversity': 'green',
    'prod_govt_cost': 'green',
    'prod_retail_profit': 'brown',
    }
import farm_model
for k,v in farm_model.activity.activities.items():
    colormap['act_' + k] = v['color']

products = ['peachesRedhaven', 'peachesOrganicRedhaven',
            'peachesBabyGold', 'peachesOrganicBabyGold', 'grapes' ]

default_demand_models = [gbm.models.DemandCurve() for k in products]
# red haven
default_demand_models[0].params['p_max'].default = 5.5
# red haven organic
default_demand_models[1].params['p_max'].default = 6.5
# baby gold
default_demand_models[2].params['p_max'].default = 5.5
# baby gold organic
default_demand_models[3].params['p_max'].default = 6.5
# grapes
default_demand_models[4].params['p_max'].default = 1.5

default_init = 'init'
for i, p in enumerate(products):
    default_init += ';sd:%s,%g,%g,%g' % (p,
        default_demand_models[i].params['p_max'].default,
        default_demand_models[i].params['p_min'].default,
        default_demand_models[i].params['slope'].default,
        )





class Server(farm_game.swi.SimpleWebInterface):
    maximum_steps = 10
    substeps_per_step = 1

    def clear(self):
        actions.clear()
        seeds.clear()
        names.clear()
        model.clear_cache()

    def swi_static(self, *path):
        if self.user is None: return
        fn = os.path.join('static', *path)
        if fn.endswith('.js'):
            mimetype = 'text/javascript'
        elif fn.endswith('.css'):
            mimetype = 'text/css'
        elif fn.endswith('.png'):
            mimetype = 'image/png'
        elif fn.endswith('.jpg'):
            mimetype = 'image/jpg'
        elif fn.endswith('.gif'):
            mimetype = 'image/gif'
        elif fn.endswith('.otf'):
            mimetype = 'font/font'
        else:
            raise Exception('unknown extenstion for %s' % fn)

        data = pkgutil.get_data('farm_game', fn)
        return (mimetype, data)

    #def swi_favicon_ico(self):
    #    icon = pkgutil.get_data('farm_game', 'static/favicon.ico')
    #    return ('image/ico', icon)

    def swi(self):
        if self.user is None:
            return self.create_login_form()
        html = pkgutil.get_data('farm_game', 'templates/overview.html')
        return html

    def swi_overview_json(self, command=None):

        if command == 'clear':
            self.clear()

        uuids = [k for k in actions.keys() if len(actions[k])>1]

        data = {k: self.run_game(k) for k in uuids}

        bar = []
        for i, uuid in enumerate(uuids):
            color = ['blue', 'red', 'green', 'magenta', 'cyan', 'black'][i % 6]

            runtime = len(data[uuid]['total_income'])

            income = sum(data[uuid]['total_income']) * 0.004 / runtime
            carbon = sum(data[uuid]['prod_carbon']) / runtime
            govt_cost = sum(data[uuid]['prod_govt_cost']) / runtime
            retail_profit = sum(data[uuid]['prod_retail_profit']) / runtime

            values = [
                dict(x=0, y=income),
                dict(x=1, y=carbon),
                dict(x=2, y=govt_cost),
                dict(x=3, y=retail_profit),
                ]


            bar.append(dict(values=values, key=names[uuid], color=color))


        return json.dumps(dict(bar=bar))

    def get_name(self, uuid):
        if isinstance(uuid, uuid_package.UUID):
            uuid = str(uuid)
        if uuid not in names:
            name = 'User %d' % (len(names) + 1)
            names[uuid] = name
        else:
            name = names[uuid]
        return name


    def swi_play(self, uuid=None, seed=None, loadactions=default_init):
        if uuid is None:
            uuid = str(uuid_package.uuid4())
        if not actions.has_key(uuid):
            actions[uuid] = []
            seeds[uuid] = uuid_package.UUID(uuid).int & 0x7fffffff
        if self.user is None:
            return self.create_login_form()
        html = pkgutil.get_data('farm_game', 'templates/play.html')
        name = self.get_name(uuid)

        if seed is not None:
            seeds[uuid] = int(seed)

        la = loadactions
        if la.startswith('init') and not la.startswith('init;'):
            la = la.replace('init', default_init)
        la = la.split('|')
        actions[uuid] = la

        return html % dict(uuid=uuid, name=name, seed=seeds[uuid],
                           action_buttons=all_actions.make_buttons(),
                           default_init=loadactions)

    def swi_set_name(self, uuid, name):
        names[uuid] = name

    def run_game(self, u):
        seed = seeds[u]
        acts = actions[u]
        print 'running', u, seed, acts


        return model.run(seed, *acts)



    def swi_play_json(self, uuid, action, seed=None, replace=None):
        name = self.get_name(uuid)
        if action.startswith('init'):
            actions[uuid] = []
        if seed is not None:
            seeds[uuid] = int(seed)

        if action == 'undo':
            if len(actions[uuid]) > 1:
                del actions[uuid][-1]
        elif action == 'reload':
            pass
        elif len(actions[uuid]) >= Server.maximum_steps:
            pass
        else:
            if replace:
                if len(actions[uuid]) > 1:
                    del actions[uuid][-1]

            actions[uuid].append(action)

        log.record(uuid, names[uuid], seeds[uuid], actions[uuid])

        return self.generate_json_data(uuid)

    def make_graph(self, data, *lines):
        result = []
        for key, label, scale in lines:
            color = colormap[key]
            values = []
            for j in range(len(data[key])):
                values.append(dict(x=float(j) / Server.substeps_per_step,
                                   y=data[key][j] * scale))
            values.append(dict(x=Server.maximum_steps, y=None))
            result.append(dict(values=values, key=label, color=color,
                               area=False))
        return result


    def generate_json_data(self, uuid):
        data = self.run_game(uuid)

        keys = [k for k in sorted(data.keys()) if k.startswith('act_')]

        time = []
        for i in range(len(keys)):
            key = keys[i]
            color = colormap[key]

            values = []
            for j in range(len(data[key])):
                values.append(dict(x=float(j)/Server.substeps_per_step, y=data[key][j]))
            values.append(dict(x=Server.maximum_steps, y=None))
            time.append(dict(values=values, key=key[4:], color=color, area=False))

        graph_money = self.make_graph(data, ('total_income', 'income', 0.004))
        graph_carbon = self.make_graph(data, ('prod_carbon', 'carbon', 1.0))
        graph_govt_cost = self.make_graph(data, ('prod_govt_cost', 'public costs', 1.0))
        graph_retail_profit = self.make_graph(data, ('prod_retail_profit', 'extra retail profit', 1.0))

        action_texts = []
        for a in actions[uuid][1:]:
            m = all_actions.find_action(a)
            if m is None:
                action_texts.append(a)
            else:
                action_texts.append(m[0].get_short_desc(m[1]))
        a = ['%d: %s' % (i+1,x) for i,x in enumerate(action_texts)]
        a = '<br/>'.join(a)

        control_text = ''
        control_code = ''
        m = all_actions.find_action(actions[uuid][-1])
        if m is not None:
            action, p = m
            control_text = action.make_control_html(p)
            control_code = action.make_control_code(p)

        grid = data['grid']

        return json.dumps(dict(time=time, grid=grid, actions=a,
                               graph_money=graph_money,
                               graph_carbon=graph_carbon,
                               graph_govt_cost=graph_govt_cost,
                               graph_retail_profit=graph_retail_profit,
                               control_text=control_text,
                               control_code=control_code))


    def create_login_form(self):
        message = "Enter the password:"
        if self.attemptedLogin:
            message = "Invalid password"
        return """<form action="/" method="POST">%s<br/>
        <input type=hidden name=swi_id value="" />
        <input type=password name=swi_pwd>
        </form>""" % message

    def swi_history(self, uuid=None):

        users = []
        for u, name in log.users.items():
            s = ' selected' if uuid == u else ''
            users.append('<option value="%s"%s>%s</option>' % (u, s, name))
        html_users = ''.join(users)


        if uuid is not None:
            items = []
            for event in log.get_events(uuid):
                t, user, username, seed, actions = event
                str_time = time.strftime('%Y/%m/%d %H:%M:%S', t)
                url = 'play?seed=%s&loadactions=%s' % (seed, ','.join(actions))
                text = '<li><a href="%s">%s %s</a></li>' % (url, str_time,
                                                            ', '.join(actions))
                items.append(text)
            html_items = 'History: <ul>%s</ul>' % ''.join(items)
        else:
            html_items = ''

        html = pkgutil.get_data('farm_game', 'templates/history.html')

        return html % dict(items=html_items, users=html_users)


    def swi_demand(self, action=None):
        html = pkgutil.get_data('farm_game', 'templates/demand.html')

        import gbm

        products = [
            ('peachesRedhaven', 'Red Haven'),
            ('peachesOrganicRedhaven', 'Organic Red Haven'),
            ('peachesBabyGold', 'Baby Gold'),
            ('peachesOrganicBabyGold', 'Baby Gold'),
            ('grapes', 'Grapes'),
            ]

        if action is None:
            models = default_demand_models
        else:
            cfg = action.split(';')
            assert len(cfg) == 5
            models = copy.deepcopy(default_demand_models)
            for i, code in enumerate(cfg):
                assert code[:3] == 'sd:'
                name, p_max, p_min, slope = code[3:].split(',')
                assert name == products[i][0]
                models[i].params['p_max'].default = float(p_max)
                models[i].params['p_min'].default = float(p_min)
                models[i].params['slope'].default = float(slope)

        d = {}
        for i, (k, title) in enumerate(products):
            d['title_%d' % i] = title
            d['key_%d' % i] = k
            d['sliders_%d' % i] = models[i].html_sliders(tag='_%d' % i)
            d['slider_keys_%d' % i] = models[i].params.keys()

        return html % d



    def swi_demand_json(self, model, index, **params):
        p = {}
        for k, v in params.items():
            if k.startswith('key_'):
                p[k[4:]] = float(v)

        import gbm
        model = getattr(gbm.models, model)()

        r = model.run(**p)
        data = model.plot_nvd3(r)

        return json.dumps(dict(main=data, index=int(index)))


    def swi_save_demand(self, name, action):
        # sanitize the string, removing invalid characters
        name = "".join(x if x.isalnum() else '_' for x in name)

        with open('save_demand_%s.txt' % name, 'w') as f:
            f.write(action)

        return self.swi_load_demand()

    def swi_load_demand(self):
        scenarios = []
        for fn in os.listdir('.'):
            if fn.startswith('save_demand_'):
                name = fn[12:-4]
                with open(fn) as f:
                    action = f.read().strip()
                scenarios.append('<li><a href="/demand?action=%s">%s</a></li>' %
                                 (action, name))
        return ''.join(scenarios)









