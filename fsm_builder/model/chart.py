class Block(object):
    def __init__(self, index, controls=None, next_block=None):
        controls = [] if controls is None else controls
        self.controls = controls
        self.next_block = next_block
        self.index = index


class Condition(object):
    def __init__(self, index, cond, true_block=None, false_block=None):
        self.index = index
        self.cond = cond
        self.true_block = true_block
        self.false_block = false_block

