import os.path
import json
import random
import uuid as uuid_package
import time

import pkgutil
import farm_game

import model
import logging
log = logging.Logging()
import actions
all_actions = actions.Actions()


from collections import OrderedDict

actions = OrderedDict()
seeds = {}
names = {}

colormap = {
    'act_peachesRedhavenConventional': 'red',
    'act_peachesRedhavenOrganic': 'pink',
    'act_peachesBabyGoldConventional': 'yellow',
    'act_peachesBabyGoldOrganic': 'gold',
    'act_grapesCoronationConventional': 'purple',
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

    }


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

        #time = []
        #for i, uuid in enumerate(uuids):
        #    color = ['blue', 'red', 'green', 'magenta', 'cyan', 'black'][i % 6]
        #    key = names[uuid]
        #    values = []
        #    for j in range(len(data[uuid]['employment'])):
        #        values.append(dict(x=float(j)/substeps, y=data[uuid]['employment'][j]))
        #    values.append(dict(x=maximum, y=None))
        #    time.append(dict(values=values, key=key, color=color, area=False))

        bar = []
        for i, uuid in enumerate(uuids):
            color = ['blue', 'red', 'green', 'magenta', 'cyan', 'black'][i % 6]
            key = names[uuid]

            '''

            employment = data[uuid]['employment'][-1]
            runtime = len(data[uuid]['production']) * 0.1
            production = sum(data[uuid]['production']) / runtime
            cost_hiring = sum(data[uuid]['cost_hiring']) / runtime
            cost_salary = sum(data[uuid]['cost_salary']) / runtime
            interv_private = sum(data[uuid]['interv_private']) / runtime
            interv_public = sum(data[uuid]['interv_public']) / runtime

            cost = cost_hiring+cost_salary+interv_private

            score = employment
            if production < cost:
                score = 0
            values = [dict(x=0, y=score), dict(x=1, y=employment)
                      ]
            '''
            values = [dict(x=0, y=100), dict(x=1, y=50)]
            bar.append(dict(values=values, key=key, color=color))


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


    def swi_play(self, uuid=None, seed=None, loadactions='init'):
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

        loadactions = loadactions.split(',')
        actions[uuid] = loadactions

        return html % dict(uuid=uuid, name=name, seed=seeds[uuid],
                           action_buttons=all_actions.make_buttons())

    def swi_set_name(self, uuid, name):
        names[uuid] = name

    def run_game(self, u):
        seed = seeds[u]
        acts = actions[u]
        print 'running', u, seed, acts


        return model.run(seed, *acts)



    def swi_play_json(self, uuid, action, seed=None, replace=None):
        name = self.get_name(uuid)
        if action == 'init':
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

    def generate_json_data(self, uuid):
        data = self.run_game(uuid)

        keys = [k for k in data.keys() if k.startswith('act_')]

        time = []
        for i in range(len(keys)):
            key = keys[i]
            color = colormap[key]

            values = []
            for j in range(len(data[key])):
                values.append(dict(x=float(j)/Server.substeps_per_step, y=data[key][j]))
            values.append(dict(x=Server.maximum_steps, y=None))
            time.append(dict(values=values, key=key[4:], color=color, area=False))


        race = []
        race_pie = []

        for k in sorted(data.keys()):
            if k.startswith('prod_'):
                key = k[5:]
                color = colormap[k]
                values = []
                for j in range(len(data[k])):
                    values.append(dict(x=float(j)/Server.substeps_per_step, y=data[k][j]))
                values.append(dict(x=Server.maximum_steps, y=None))
                race.append(dict(values=values, key=key, color=color, area=False))

                #p = data['proportion_%s' % key]
                #race_pie.append(dict(label=key, value=p[-1], color=color))


        grid = data['grid']


        money = []
        '''
        runtime = len(data['production']) * 0.1
        production = sum(data['production']) / runtime
        cost_hiring = sum(data['cost_hiring']) / runtime
        cost_salary = sum(data['cost_salary']) / runtime
        interv_private = sum(data['interv_private']) / runtime
        interv_public = sum(data['interv_public']) / runtime
        money.append(dict(key='production', values=[{'x':0, 'y':production}, {'x':1, 'y':0}, {'x':2, 'y':0}]))
        money.append(dict(key='hiring', values=[{'x':0, 'y':0}, {'x':1, 'y':cost_hiring}, {'x':2, 'y':0}]))
        money.append(dict(key='salary', values=[{'x':0, 'y':0}, {'x':1, 'y':cost_salary}, {'x':2, 'y':0}]))
        money.append(dict(key='intervention', values=[{'x':0, 'y':0}, {'x':1, 'y':interv_private}, {'x':2, 'y':interv_public}]))
        '''

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


        return json.dumps(dict(time=time, race=race, race_pie=race_pie,
                               grid=grid, money=money, actions=a,
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


