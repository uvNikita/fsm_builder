import sys
import os
from tempfile import mktemp

import pydot
from gi.repository import Gtk

from .model.input import InputAlg
from .model.chart import Block, Condition, get_blocks

builder = Gtk.Builder()
module = sys.modules.get('fsm_builder').__file__
gui_file = os.path.join(os.path.dirname(module),
                        os.path.pardir, 'gui.glade')
builder.add_from_file(gui_file)

alg_holder = builder.get_object('alg_label')
input_alg = InputAlg(alg_holder)

chart_file = mktemp('.png', 'fsm_chart_', '/tmp/')


def draw_chart(chart):
    blocks = get_blocks(chart)
    G = pydot.Dot('graphname', graph_type='digraph', rankdir='TB', size=100)
    for block in blocks.values():
        if isinstance(block, Block):
            G.add_node(pydot.Node(str(block), shape='box'))
        elif isinstance(block, Condition):
            G.add_node(pydot.Node(str(block), shape='diamond'))

    for block in blocks.values():
        if isinstance(block, Block) and block.next_block:
            G.add_edge(pydot.Edge(str(block), str(block.next_block)))
        elif isinstance(block, Condition):
            G.add_edge(pydot.Edge(str(block), str(block.true_block), label='True'))
            G.add_edge(pydot.Edge(str(block), str(block.false_block), label='False'))
    G.write_png(chart_file)

