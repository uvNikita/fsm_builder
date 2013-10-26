import json
from math import ceil, log2
from itertools import count

import pydot


class Node(object):
    def __init__(self, idx, code=None, fake=False):
        self.idx = idx
        self.code = code
        self.fake = fake

    def __repr__(self):
        return "Z{}[{}]".format(self.idx, self.code or '')

    def __str__(self):
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


class CodesError(Exception):
    pass


class MealyGraph(object):
    def __init__(self, holder, graph_file):
        self.holder = holder
        self.graph_file = graph_file
        self.nodes = []
        self.connections = []

    def fill(self, nodes, connections):
        self.nodes = list(nodes)
        self.connections = list(connections)
        self.put_codes()

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
        self.fill(nodes.values(), conns)

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
        graph = pydot.Dot('alg_graph')
        for node in self.nodes:
            if node.fake:
                graph.add_node(pydot.Node(str(node), xlabel=node.code, style='dashed'))
            else:
                graph.add_node(pydot.Node(str(node), xlabel=node.code))

        for conn in self.connections:
            graph.add_edge(pydot.Edge(str(conn.frm), str(conn.to), label=str(conn)))

        graph.write_png(self.graph_file)
        self.holder.set_from_file(self.graph_file)

    def put_codes(self):
        def gen_codes(ln):
            bin_codes = map(lambda c: bin(c)[2:], range(2 ** ln))
            return list(map(lambda c: ('0' * ln + c)[-ln:], bin_codes))

        def diff(code1, code2):
            diffs = 0
            for c1, c2 in zip(code1, code2):
                if c1 != c2:
                    diffs += 1
            return diffs

        def find_path(from_code, to_code, free_codes):
            if diff(from_code, to_code) == 1:
                return ()
            one_diff_codes = filter(lambda c: diff(c, from_code) == 1, free_codes)
            paths = []
            for code in one_diff_codes:
                path = find_path(code, to_code, free_codes - {code})
                if path is not None:
                    paths.append((code,) + path)
            return min(paths, key=len) if paths else None

        def try_put_codes(ln):
            def get_code(node, codes, nodes, connections):
                idx_gen = count(max([n.idx for n in nodes]) + 1)
                free_codes = all_codes - set(codes.values())
                from_nodes = set([c.to for c in filter(lambda c: c.frm is node, connections)])
                to_nodes = set([c.frm for c in filter(lambda c: c.to is node, connections)])
                bcodes_from = {
                    bnode: codes[bnode]
                    for bnode in from_nodes
                    if bnode in codes
                }
                bcodes_to = {
                    bnode: codes[bnode]
                    for bnode in to_nodes
                    if bnode in codes
                }
                for free_code in free_codes:
                    new_free_codes = free_codes
                    new_nodes = nodes
                    new_connections = connections
                    new_codes = codes.copy()
                    valid = True
                    for bnode, bcode in bcodes_from.items():
                        path = find_path(free_code, bcode, new_free_codes - {free_code})
                        # Can't create path even with fake nodes, breaking
                        if path is None:
                            valid = False
                            break
                        fake_nodes = []
                        for code in path:
                            fake_node = Node(next(idx_gen), fake=True)
                            fake_nodes.append(fake_node)
                            new_codes[fake_node] = code
                        fake_nodes = tuple(fake_nodes)

                        if not fake_nodes:
                            continue

                        new_nodes += fake_nodes
                        old_conn = next(conn for conn in new_connections if conn.frm is node and conn.to is bnode)
                        # Remove old connection
                        new_connections = tuple(filter(lambda c: c is not old_conn, new_connections))

                        # First connection node -> fake
                        new_connections += (Connection(old_conn.ctrls, node, fake_nodes[0], old_conn.cond),)
                        # Last connection fake -> bnode
                        new_connections += (Connection([], fake_nodes[-1], bnode),)

                        for prev_node, curr_node in zip(fake_nodes, fake_nodes[1:]):
                            new_connections += (Connection([], prev_node, curr_node),)
                        new_free_codes = new_free_codes - set(path)

                    if not valid:
                        continue
                    for bnode, bcode in bcodes_to.items():
                        path = find_path(bcode, free_code, new_free_codes - {free_code})
                        # Can't create path even with fake nodes, breaking
                        if path is None:
                            valid = False
                            break
                        fake_nodes = []
                        for code in path:
                            fake_node = Node(next(idx_gen), fake=True)
                            fake_nodes.append(fake_node)
                            new_codes[fake_node] = code
                        fake_nodes = tuple(fake_nodes)

                        if not fake_nodes:
                            continue

                        new_nodes += fake_nodes
                        old_conn = next(conn for conn in new_connections if conn.frm is bnode and conn.to is node)
                        # Remove old connection
                        new_connections = tuple(filter(lambda c: c is not old_conn, new_connections))

                        # First connection bnode -> fake
                        new_connections += (Connection(old_conn.ctrls, bnode, fake_nodes[0], old_conn.cond),)
                        # Last connection fake -> node
                        new_connections += (Connection([], fake_nodes[-1], node),)

                        for prev_node, curr_node in zip(fake_nodes, fake_nodes[1:]):
                            new_connections += (Connection([], prev_node, curr_node),)
                        new_free_codes = new_free_codes - set(path)

                    if valid:
                        new_codes[node] = free_code
                        return new_codes, new_nodes, new_connections
                raise CodesError("No suitable code found")

            all_codes = set(gen_codes(ln))
            connections = tuple(self.connections)
            nodes = tuple(self.nodes)
            codes = {}
            for node in nodes:
                code = codes.get(node)
                if not code:
                    codes, nodes, connections = get_code(node, codes, nodes, connections)
            return list(nodes), list(connections), codes

        ln = ceil(log2(len(self.nodes)))
        while True:
            try:
                nodes, connnections, codes = try_put_codes(ln)
            except CodesError:
                ln += 1
                continue
            for node, code in codes.items():
                node.code = code
            self.nodes = nodes
            self.connections = connnections
            return
