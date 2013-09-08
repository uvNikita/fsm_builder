from ..util import superscripted, underscripted


class JumpFrom(object):
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '↑{id}'.format(id=superscripted(str(self.id)))


class JumpTo(object):
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '↓{id}'.format(id=superscripted(str(self.id)))


class Condition(object):
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return 'X{id}'.format(id=underscripted(str(self.id)))


class Node(object):
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return 'Y{id}'.format(id=underscripted(str(self.id)))


class End(object):
    def __repr__(self):
        return 'E'
