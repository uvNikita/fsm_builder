class Block(object):
    def __init__(self, index, controls=None, next_block=None):
        controls = [] if controls is None else controls
        self.controls = controls
        self.next_block = next_block
        self.index = index

    def __repr__(self):
        if self.index == 0:
            label = 'Begin'
        elif not self.controls:
            label = 'End'
        else:
            label = ','.join(['Y{}'.format(ctrl) for ctrl in self.controls])
        return '{idx}.{label}'.format(idx=self.index, label=label)


class Condition(object):
    def __init__(self, index, cond, true_block=None, false_block=None):
        self.index = index
        self.cond = cond
        self.true_block = true_block
        self.false_block = false_block

    def __repr__(self):
        return '{idx}.X{cond}'.format(idx=self.index, cond=self.cond)


def get_blocks(chart):
    blocks = {}

    def parse(block):
        if blocks.get(block.index):
            return
        else:
            blocks[block.index] = block
        if isinstance(block, Block) and block.next_block:
            parse(block.next_block)
        elif isinstance(block, Condition):
            parse(block.true_block)
            parse(block.false_block)
    parse(chart)
    return blocks
