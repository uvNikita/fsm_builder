from . import chart
from . import input
from . import graph


class ParseError(Exception):
    def __init__(self, idx=None, *args, **kwargs):
        super(ParseError, self).__init__(*args, **kwargs)
        self.idx = idx


def input_to_chart(input_alg: input.InputAlg) -> chart.Block:
    """
    Converts algorithm from input to chart type
    """
    # get indexes of all JumpTo
    jump_to = {}
    for loc, action in enumerate(input_alg):
        if isinstance(action, input.JumpTo):
            jump_to[action.index] = loc + 1

    # General validation
    if not isinstance(input_alg[0], input.Begin):
        raise ParseError(0, "First block must be Begin")

    if not any(isinstance(act, input.End) for act in input_alg):
        raise ParseError(len(input_alg) - 1, "There is no End block in algorithm")

    if len(input_alg) == 2:
        raise ParseError(0, "Algorithm has only Begin and End block")

    blocks = {}
    block_id = 0

    def parse(curr, prev):
        nonlocal block_id
        if not input_alg.has(curr):
            raise ParseError(prev, "Unexpected end of input")
        curr_action = input_alg[curr]
        if blocks.get(curr):
            return blocks[curr]

        block = None
        if isinstance(curr_action, input.Begin):
            block = chart.Block(block_id)
            blocks[curr] = block
            block_id += 1
            block.next_block = parse(curr + 1, curr)
        elif isinstance(curr_action, input.End):
            block = chart.Block(block_id)
            blocks[curr] = block
            block_id += 1
        elif isinstance(curr_action, input.Condition):
            block = chart.Condition(block_id, curr_action.index)
            blocks[curr] = block
            block_id += 1
            if not input_alg.has(curr + 1):
                raise ParseError(curr, "Unexpected end of input")
            jump = input_alg[curr + 1]
            if not isinstance(jump, input.JumpFrom):
                raise ParseError(curr + 1, "After condition must be jump")
            if jump.index not in jump_to:
                raise ParseError(curr + 1, "Do not know where to jump")
            if not input_alg.has(jump_to[jump.index]):
                raise ParseError(jump_to[jump.index] - 1, "Do not know where to jump")
            block.true_block = parse(jump_to[jump.index], curr)
            block.false_block = parse(curr + 2, curr)
        elif isinstance(curr_action, input.Control):
            block = chart.Block(block_id, controls=[curr_action.index])
            blocks[curr] = block
            block_id += 1
            block.next_block = parse(curr + 1, curr)
        elif isinstance(curr_action, input.ControlBlock):
            controls = [control.index for control in curr_action.controls]
            block = chart.Block(block_id, controls=controls)
            blocks[curr] = block
            block_id += 1
            block.next_block = parse(curr + 1, curr)
        elif isinstance(curr_action, input.JumpFrom):
            if curr_action.index not in jump_to:
                raise ParseError(curr, "Do not know where to jump")
            return parse(jump_to[curr_action.index], curr)
        elif isinstance(curr_action, input.JumpTo):
            return parse(curr + 1, curr)

        if not block:
            raise ValueError("invalid input action:", curr_action)
        return block

    chart_alg = parse(0, 0)

    # Check lonely blocks
    crtls = [
        idx for idx, ctrl in enumerate(input_alg)
        if isinstance(ctrl, (input.Control, input.ControlBlock, input.Begin, input.End))
    ]
    lonely = next((ctrl for ctrl in crtls if ctrl not in blocks), None)
    if lonely is not None:
        raise ParseError(lonely, "Lonely controls")

    return chart_alg


def chart_to_tables(chart_alg: chart.Block) -> dict:
    def_table = dict()

    blocks = chart.get_blocks(chart_alg)
    con_table = [[0 for _ in blocks] for _ in blocks]

    for idx, block in blocks.items():
        if isinstance(block, chart.Block):
            def_table[idx] = block.controls or '-'
            if block.next_block:
                con_table[idx][block.next_block.index] = 1
        elif isinstance(block, chart.Condition):
            def_table[idx] = [block.cond]
            con_table[idx][block.true_block.index] = 1
            con_table[idx][block.false_block.index] = 2
    return def_table, con_table


def chart_to_graph(chart_alg: chart.Block) -> tuple:
    nodes = {}
    node_idx = 0

    def create_nodes(block, was_ctrl):
        nonlocal node_idx
        if block.index in nodes:
            return
        if was_ctrl:
            # End block case
            if isinstance(block, chart.Block) and not block.next_block:
                nodes[block.index] = nodes[chart_alg.next_block.index]
            else:
                nodes[block.index] = graph.Node(node_idx)
                node_idx += 1
        if isinstance(block, chart.Block):
            if block.next_block:
                create_nodes(block.next_block, True)
        elif isinstance(block, chart.Condition):
            create_nodes(block.true_block, False)
            create_nodes(block.false_block, False)

    create_nodes(chart_alg, False)

    conns = []
    passed = []

    def create_conns(block, prev_node, cond, ctrls):
        nonlocal conns, passed
        new_cond = cond
        new_ctrls = ctrls
        new_node = prev_node
        if block.index in nodes:
            node = nodes[block.index]
            if prev_node:
                conns.append(graph.Connection(ctrls,
                                              frm=prev_node, to=node,
                                              cond=cond))
                new_cond = []
                new_ctrls = []
            new_node = node

        if block in passed:
            return
        else:
            passed.append(block)

        if isinstance(block, chart.Block):
            if block.next_block:
                create_conns(block.next_block, new_node, new_cond, new_ctrls + block.controls)
        elif isinstance(block, chart.Condition):
            new_x = graph.Condition(block.cond, True)
            create_conns(block.true_block, new_node, new_cond + [new_x], new_ctrls)
            new_x = graph.Condition(block.cond, False)
            create_conns(block.false_block, new_node, new_cond + [new_x], new_ctrls)

    create_conns(chart_alg, None, [], [])

    return nodes, conns


JK_TABLE = {
    (0, 0): (0, None),
    (0, 1): (1, None),
    (1, 0): (None, 1),
    (1, 1): (None, 0)
}


def graph_to_trans_table(input_graph):
    nodes, conns = input_graph
    table = []
    all_ctrls = set(ctrl for c in conns for ctrl in c.ctrls)
    all_conds = set(cond.idx for conn in conns for cond in conn.cond)
    for conn in conns:
        row = {}
        row['from_name'] = str(conn.frm)
        row['from_code'] = conn.frm.code
        row['to_name'] = str(conn.to)
        row['to_code'] = conn.to.code
        cond = {cond.idx: cond.value for cond in conn.cond}
        row['cond'] = {cond_id: cond.get(cond_id) for cond_id in all_conds}
        row['ctrls'] = {ctrl: ctrl in conn.ctrls for ctrl in all_ctrls}
        row['trig'] = []
        for fc, tc in zip(conn.frm.code, conn.to.code):
            row['trig'].append(JK_TABLE[int(fc), int(tc)])
        table.append(row)
    return table
