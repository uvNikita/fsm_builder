class Node(object):
    def __init__(self, idx):
        self.idx = idx

    def __repr__(self):
        return "Z{}".format(self.idx)


class Condition(object):
    def __init__(self, idx, value):
        self.idx = idx
        self.value = value

    def __repr__(self):
        if self.value:
            return "X{}".format(self.idx)
        else:
            return "!X{}".format(self.idx)


class Connection(object):
    def __init__(self, ctrls, frm, to, cond=None):
        self.ctrls = ctrls
        self.frm = frm
        self.to = to
        self.cond = cond or []

    def __repr__(self):
        return "{frm} --({signals})-> {to}".format(
            frm=self.frm, signals=str(self), to=self.to
        )

    def __str__(self):
        ctrls_str = (
            ','.join(['Y{}'.format(ctrl) for ctrl in self.ctrls])
            if self.ctrls else '-'
        )
        conds_str = (
            ''.join(map(str, self.cond))
            if self.cond else '-'
        )
        return "{}/{}".format(ctrls_str, conds_str)
