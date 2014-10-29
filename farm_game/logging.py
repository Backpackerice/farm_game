import time


class Logging(object):
    def __init__(self, filename=None):
        if filename is None:
            filename = time.strftime('log-%Y%m%d-%H%M%S.txt')
        self.filename = filename
        self.users = {}

    def record(self, user, username, seed, actions):
        t = time.strftime('%Y%m%d-%H%M%S')

        # make sure there's no commas in the username, as that will complicate
        # parsing the log later
        username = username.replace(',', ' ')

        line = '%s, %s, %s, %s, %s\n' % (t, user, username, seed,
                                        ','.join(actions))

        with open(self.filename, 'a') as f:
            f.write(line)

        self.users[user] = username

    def get_events(self, userid):
        data = []
        try:
            f = open(self.filename)
        except IOError:
            return []
        for line in f.readlines():
            line = line.strip().split(', ')
            t, user, username, seed, actions = line
            if userid is None or user == userid:
                t = time.strptime(t, '%Y%m%d-%H%M%S')
                actions = actions.split(',')
                data.append((t, user, username, seed, actions))
        f.close()
        return data





