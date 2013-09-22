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

    def append(self, action):
        self.alg.append(action)

    def pop(self, *args, **kwargs):
        if len(self.alg) > 1:
            return self.alg.pop(*args, **kwargs)

    def new(self):
        self.alg = [Begin()]

    def draw(self, *, errors=()):
        res = ''
        for idx, action in enumerate(self.alg):
            action_str = str(action)
            if idx in errors:
                action_str = "<span foreground='red'>{}</span>".format(action_str)
            res += action_str
        self.holder.set_markup(res)

    def __iter__(self):
        return iter(self.alg)

    def __getitem__(self, item):
        return self.alg[item]

    def __len__(self):
        return len(self.alg)

    def __repr__(self):
        return ''.join(map(str, self.alg))
