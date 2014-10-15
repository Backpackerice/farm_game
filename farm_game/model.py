from collections import OrderedDict

class Model:
    employer_count = 10
    people_per_step = 1
    years_per_step = 0.1
    max_age = 25

    def __init__(self, seed=None):
        self.rng = np.random.RandomState(seed=seed)
        self.society = Society(self.rng)
        self.employers = [Employer(self.society)
                          for i in range(self.employer_count)]
        self.people = []
        self.steps = 0
        self.interventions = []
        self.data = {}
        self.init_data()

    def step(self):
        self.steps += 1
        for interv in self.interventions:
            interv.apply(self, self.steps)

        for i in range(self.people_per_step):
            self.people.append(Person(self.society))


        applications = OrderedDict()
        for e in self.employers:
            for j in e.jobs:
                if j.employee is None:
                    applications[j] = []
        for p in self.people:
            if p.job is None:
                for j in applications.keys():
                    if p.does_apply(j):
                        applications[j].append(p)

        interview = {}
        for job, applicants in applications.items():
            for a in applicants:
                score = job.compute_suitability(a)
                score += self.rng.normal(a.attributes['interview_skill'],
                                         a.attributes['interview_skill_sd'])
                interview[(job, a)] = score

        iterations = 4
        for i in range(iterations):
            all_offers = OrderedDict()
            for job, applicants in applications.items():

                score = [interview[(job, a)] for a in applicants]

                if len(score) > 0:
                    max_score = max(score)
                    if max_score > 0:
                        index = score.index(max_score)
                        person = applicants[index]
                        if person not in all_offers:
                            all_offers[person] = []
                        all_offers[person].append(job)

            for person, offers in all_offers.items():
                score = [person.compute_suitability(j) for j in offers]
                if len(score) > 0:
                    max_score = max(score)
                    if max_score > 0:
                        index = score.index(max_score)
                        job = offers[index]

                        person.job = job
                        job.employee = person
                        self.society.interv_public += self.society.get_job_cost_public
                        self.society.interv_private += self.society.get_job_cost_private
                        person.job_evaluation = 'medium'
                        person.job_length = 0.0

        for e in self.employers:
            e.step(self.years_per_step)
        self.increase_age()
        self.remove_older()
        self.job_evaluation()

        self.update_data()

    def job_evaluation(self):
        for p in self.people:
            if p.job is not None:
                index = int(p.job_length)
                retention = self.society.job_retention[p.job.type]
                if index >= len(retention):
                    r = retention[-1]
                else:
                    r = retention[index]
                r = (1-r) * self.years_per_step
                if self.society.rng.rand() < r:
                    self.fire(p)

    def fire(self, person):
        assert person.job is not None
        person.job.employee = None
        person.job = None
        person.job_length = 0.0



    def increase_age(self):
        for p in self.people:
            p.age += self.years_per_step
            p.job_length += self.years_per_step
            if p.job is not None:
                p.attributes['experience'] += self.years_per_step
                sector = self.society.job_sector[p.job.type]
                p.attributes['experience_%s' % sector] += self.years_per_step
            else:
                p.attributes['unemployed_time'] += self.years_per_step
            p.attributes['age'] = p.age

    def remove_older(self):
        for p in self.people:
            if p.age > self.max_age:
                p.neighbourhood.free_location(p.location)
                self.people.remove(p)
                if p.job is not None:
                    p.job.employee = None


    def calc_employment(self):
        count = 0
        for p in self.people:
            if p.job is not None:
                count += 1
        return float(count)/len(self.people)

    def calc_feature_employment(self, feature):
        count = 0
        total = 0
        for p in self.people:
            if feature in p.features:
                total += 1
                if p.job is not None:
                    count += 1
        if total == 0: return 0
        return float(count) / total

    def calc_attribute_employment(self, attribute, threshold):
        count = 0
        total = 0
        for p in self.people:
            if p.attributes[attribute] >= threshold:
                total += 1
                if p.job is not None:
                    count += 1
        if total == 0: return 0
        return float(count) / total

    def calc_feature_rate(self, feature):
        count = 0
        for p in self.people:
            if feature in p.features:
                count += 1
        return float(count)/len(self.people)

    def calc_attribute_rate(self, attribute, threshold):
        count = 0
        for p in self.people:
            if p.attributes[attribute] >= threshold:
                count += 1
        return float(count)/len(self.people)

    def calc_employer_net(self):
        return sum([e.net for e in self.employers])


    def check_jobs(self):
        for p in self.people:
            print p.features, p.job.type if p.job is not None else None
        #for e in self.employers:
        #    print e.total_net

    def init_data(self):
        self.data['employment'] = []
        self.data['employer_net'] = []
        self.data['highschool'] = []
        self.data['employment_childcare'] = []
        self.data['employment_nohighschool'] = []
        self.data['employment_2_or_more_years'] = []
        self.data['employment_18plus'] = []
        self.data['proportion_childcare'] = []
        self.data['proportion_nohighschool'] = []
        self.data['proportion_2_or_more_years'] = []
        self.data['proportion_18plus'] = []

        self.data['cost_hiring'] = []
        self.data['cost_salary'] = []
        self.data['production'] = []
        self.data['interv_public'] = []
        self.data['interv_private'] = []

        #for race in self.society.race.keys():
        #    self.data['employment_%s' % race] = []
        #    self.data['proportion_%s' % race] = []

    def update_data(self):
        if self.steps >= 100:
            self.data['employment'].append(self.calc_employment()*100)
            self.data['employer_net'].append(self.calc_employer_net()*0.001)
            self.data['highschool'].append(self.calc_feature_rate('highschool')*100)
            self.data['employment_childcare'].append(self.calc_feature_employment('childcare')*100)
            self.data['employment_nohighschool'].append(self.calc_feature_employment('no_highschool')*100)
            self.data['employment_2_or_more_years'].append(self.calc_attribute_employment('experience', threshold=2.0)*100)
            self.data['employment_18plus'].append(self.calc_attribute_employment('age', threshold=18)*100)
            self.data['proportion_childcare'].append(self.calc_feature_rate('childcare')*100)
            self.data['proportion_nohighschool'].append(self.calc_feature_rate('no_highschool')*100)
            self.data['proportion_2_or_more_years'].append(self.calc_attribute_rate('experience', threshold=2.0)*100)
            self.data['proportion_18plus'].append(self.calc_attribute_rate('age', threshold=18)*100)
            self.data['cost_hiring'].append(sum([e.hiring_cost for e in self.employers]))
            self.data['cost_salary'].append(sum([e.salary for e in self.employers]))
            self.data['production'].append(sum([e.productivity for e in self.employers]))
            self.data['interv_public'].append(self.society.interv_public)
            self.data['interv_private'].append(self.society.interv_private)
            #for race in self.society.race.keys():
            #    self.data['employment_%s' % race].append(self.calc_feature_employment(race)*100)
            #    self.data['proportion_%s' % race].append(self.calc_feature_rate(race)*100)

    def get_grid(self):
        grid = []
        for e in self.employers:
            x, y = self.get_location(e)
            color = e.get_color()
            item = dict(type='employer', x=x, y=y, color=color, info=e.get_info())
            grid.append(item)
        for p in self.people:
            x, y = self.get_location(p)
            color = p.get_color()
            item = dict(type='person', x=x, y=y, color=color, info=p.get_info())
            grid.append(item)
        return grid

    def get_location(self, item):
        xx, yy = item.location
        n_index = self.society.neighbourhoods.index(item.neighbourhood)
        x = (n_index % self.society.neighbourhood_cols) * item.neighbourhood.cols + xx
        y = (n_index / self.society.neighbourhood_cols) * item.neighbourhood.rows + yy
        return x, y

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
    presteps = 100
    for i in range(presteps):
        model.step()
    model_cache[(seed, ())] = copy.deepcopy(model)
    return -1, model

@memoize
def run(seed, *actions):
    step, model = find_cached_model(seed, actions)
    return model.get_data()


if __name__ == '__main__':
    print 1
    run(1, 'init')
    print 2
    clear_cache()
    print 3
    run(1, 'init')
    print 4

    1/0



    m = Model()

    m.interventions.append(HighschoolCertificateIntervention(50, 1.0))
    m.step()

    for i in range(1000):
        print i, len(m.people), m.calc_employment()
        m.check_jobs()
        m.step()




