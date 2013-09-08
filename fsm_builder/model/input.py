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

    def new(self):
        self.alg = [Begin()]

    def draw(self):
        self.holder.set_text(str(self))

    def __repr__(self):
        return ''.join(map(str, self.alg))
