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

files = {
    'data_file': None,
    'chart_file': mktemp('.png', 'fsm_chart_', '/tmp/')
}


def draw_chart(chart):
    blocks = get_blocks(chart)
    graph = pydot.Dot('alg_chart', graph_type='digraph', rankdir='TB', size=100)
    for block in blocks.values():
        if isinstance(block, Block):
            graph.add_node(pydot.Node(str(block), shape='box'))
        elif isinstance(block, Condition):
            graph.add_node(pydot.Node(str(block), shape='diamond'))

    for block in blocks.values():
        if isinstance(block, Block) and block.next_block:
            graph.add_edge(pydot.Edge(str(block), str(block.next_block)))
        elif isinstance(block, Condition):
            graph.add_edge(pydot.Edge(str(block), str(block.true_block), label='True'))
            graph.add_edge(pydot.Edge(str(block), str(block.false_block), label='False'))
    graph.write_png(files['chart_file'])

