from ..util import superscripted, underscripted


class JumpFrom(object):
    def __init__(self, index):
        self.index = index

    def __repr__(self):
        return '↑{id}'.format(id=superscripted(str(self.index)))


class JumpTo(object):
    def __init__(self, index):
        self.index = index

    def __repr__(self):
        return '↓{id}'.format(id=superscripted(str(self.index)))


class Condition(object):
    def __init__(self, index):
        self.index = index

    def __repr__(self):
        return 'X{id}'.format(id=underscripted(str(self.index)))


class Control(object):
    def __init__(self, index):
        self.index = index

    def __repr__(self):
        return 'Y{id}'.format(id=underscripted(str(self.index)))


class ControlBlock(object):
    def __init__(self, ids):
        self.controls = [Control(index) for index in ids]

    def __repr__(self):
        return '({})'.format(','.join(map(str, self.controls)))


class End(object):
    def __repr__(self):
        return 'E'


class Begin(object):
    def __repr__(self):
        return 'B'


class InputAlg(object):
    def __init__(self, holder, actions=None):
        actions = [Begin()] if actions is None else actions
        self.holder = holder
        self.alg = list(actions)
        self.curr_pos = 0

    def insert(self, action):
        self.curr_pos += 1
        self.alg.insert(self.curr_pos, action)

    def delete(self):
        # Do not allow to remove begin
        if self.curr_pos == 0:
            return
        if len(self.alg) > 1:
            self.alg.pop(self.curr_pos)
            if not self.has(self.curr_pos):
                self.curr_pos -= 1

    def new(self):
        self.alg = [Begin()]
        self.curr_pos = 0

    def load_alg(self, alg):
        self.curr_pos = 0
        self.alg = alg

    def move_left(self):
        if self.has(self.curr_pos - 1):
            self.curr_pos -= 1

    def move_right(self):
        if self.has(self.curr_pos + 1):
            self.curr_pos += 1

    def draw(self, *, errors=()):
        res = ''
        for idx, action in enumerate(self.alg):
            action_str = str(action)
            color = None
            if idx == self.curr_pos:
                color = 'grey'
            elif idx in errors:
                color = 'red'
            if color:
                action_str = "<span foreground='{}'>{}</span>".format(color, action_str)
            res += action_str
        self.holder.set_markup(res)

    def has(self, idx):
        return 0 <= idx < len(self.alg)

    def __iter__(self):
        return iter(self.alg)

    def __getitem__(self, item):
        return self.alg[item]

    def __len__(self):
        return len(self.alg)

    def __repr__(self):
        return ''.join(map(str, self.alg))
