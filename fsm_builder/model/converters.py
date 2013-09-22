from collections import defaultdict
import fsm_builder.model.chart as chart
import fsm_builder.model.input as input


def input_to_chart(input_alg: input.InputAlg) -> chart.Block:
    """
    Converts algorithm from input to chart type
    """
    # get indexes of all JumpTo
    jump_to = {}
    for loc, action in enumerate(input_alg):
        if isinstance(action, input.JumpTo):
            jump_to[action.index] = loc + 1

    blocks = {}
    block_id = 0

    def parse(curr):
        nonlocal block_id
        curr_action = input_alg[curr]
        if blocks.get(curr):
            return blocks[curr]

        block = None
        if isinstance(curr_action, input.Begin):
            block = chart.Block(block_id)
            blocks[curr] = block
            block_id += 1
            block.next_block = parse(curr + 1)
        elif isinstance(curr_action, input.End):
            block = chart.Block(block_id)
            blocks[curr] = block
            block_id += 1
        elif isinstance(curr_action, input.Condition):
            block = chart.Condition(block_id, curr_action.index)
            blocks[curr] = block
            block_id += 1
            jump_id = input_alg[curr + 1].index
            block.true_block = parse(jump_to[jump_id])
            block.false_block = parse(curr + 2)
        elif isinstance(curr_action, input.Control):
            block = chart.Block(block_id, controls=[curr_action.index])
            blocks[curr] = block
            block_id += 1
            block.next_block = parse(curr + 1)
        elif isinstance(curr_action, input.ControlBlock):
            controls = [control.index for control in curr_action.controls]
            block = chart.Block(block_id, controls=controls)
            blocks[curr] = block
            block_id += 1
            block.next_block = parse(curr + 1)
        elif isinstance(curr_action, input.JumpFrom):
            return parse(jump_to[curr_action.index])
        elif isinstance(curr_action, input.JumpTo):
            return parse(curr + 1)

        if not block:
            raise ValueError("invalid input action:", curr_action)
        return block

    return parse(0)


def chart_to_tables(chart_alg: chart.Block) -> dict:
    con_table = defaultdict(list)
    def_table = dict()

    blocks = chart.get_blocks(chart_alg)
    for idx, block in blocks.items():
        if isinstance(block, chart.Block):
            def_table[idx] = block.controls or '-'
        elif isinstance(block, chart.Condition):
            def_table[idx] = [block.cond]

    def parse(block):
        if con_table.get(block.index):
            return
        if isinstance(block, chart.Block) and block.next_block:
            con_table[block.index].append(block.next_block.index)
            parse(block.next_block)
        elif isinstance(block, chart.Condition):
            con_table[block.index].append(block.true_block.index)
            parse(block.true_block)
            con_table[block.index].append(block.false_block.index)
            parse(block.false_block)
    parse(chart_alg)
    return def_table, dict(con_table)