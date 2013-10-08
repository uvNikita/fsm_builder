import json
import pydot


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
        return "{frm} -({signals})-> {to}".format(
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
        return "{}/{}".format(conds_str, ctrls_str)


class MealyGraph(object):
    def __init__(self, holder, graph_file):
        self.holder = holder
        self.graph_file = graph_file
        self.nodes = []
        self.connections = []

    def fill(self, nodes, connections):
        self.nodes = nodes
        self.connections = connections

    def load(self, fp):
        graph_dict = json.load(fp)
        nodes = {node_idx: Node(node_idx) for node_idx in graph_dict['nodes']}
        conns = []
        for conn_dict in graph_dict['connections']:
            ctrls = conn_dict['ctrls']
            frm = nodes[conn_dict['from']]
            to = nodes[conn_dict['to']]
            cond = [
                Condition(cond_dict['idx'], cond_dict['value'])
                for cond_dict in conn_dict['cond']
            ]
            conns.append(Connection(ctrls, frm, to, cond))
        self.nodes = nodes.values()
        self.connections = conns

    def dump(self, fp):
        graph_dict = {}
        node_idxs = [node.idx for node in self.nodes]
        graph_dict['nodes'] = node_idxs

        conns = [
            {'from': conn.frm.idx,
             'to': conn.to.idx,
             'ctrls': conn.ctrls,
             'cond': [cond.__dict__ for cond in conn.cond]}
            for conn in self.connections
        ]
        graph_dict['connections'] = conns
        return json.dump(graph_dict, fp)

    def draw(self):
        graph = pydot.Dot('alg_graph', graph_type='digraph', rankdir='TB', size=100)
        for node in self.nodes:
            graph.add_node(pydot.Node(str(node)))

        for conn in self.connections:
            graph.add_edge(pydot.Edge(str(conn.frm), str(conn.to), label=str(conn)))

        graph.write_png(self.graph_file)
        self.holder.set_from_file(self.graph_file)
