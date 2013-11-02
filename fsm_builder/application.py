import sys
import os
from tempfile import mktemp

import pydot
from gi.repository import Gtk

from .model.input import InputAlg
from .model.chart import Block, Condition, get_blocks
from .model.graph import MealyGraph
from .model.trans_table import TransTable

builder = Gtk.Builder()
module = sys.modules.get('fsm_builder').__file__

files = {
    'data_file': None,
    'chart_file': mktemp('.png', 'fsm_chart_', '/tmp/'),
    'graph_file': mktemp('.png', 'fsm_graph_', '/tmp/'),
    'gui_file': os.path.join(os.path.dirname(module),
                             os.path.pardir, 'gui.glade')
}

builder.add_from_file(files['gui_file'])

alg_holder = builder.get_object('alg_label')
input_alg = InputAlg(alg_holder)

graph_holder = builder.get_object('graph')
fsm_graph = MealyGraph(graph_holder, files['graph_file'])

trans_holder = builder.get_object('trans_view')
triggers_holder = builder.get_object('triggers_view')
trans_table = TransTable(trans_holder, triggers_holder)


def draw_chart(chart, nodes):
    blocks = get_blocks(chart)
    graph = pydot.Dot('alg_chart')
    for block in blocks.values():
        if isinstance(block, Block):
            graph.add_node(pydot.Node(str(block), shape='box'))
        elif isinstance(block, Condition):
            graph.add_node(pydot.Node(str(block), shape='diamond'))

    for block in blocks.values():
        if isinstance(block, Block) and block.next_block:
            if block.next_block.index in nodes:
                label = str(nodes[block.next_block.index])
            else:
                label = ''
            graph.add_edge(pydot.Edge(str(block), str(block.next_block), label=label))
        elif isinstance(block, Condition):
            graph.add_edge(pydot.Edge(str(block), str(block.true_block), label='True'))
            graph.add_edge(pydot.Edge(str(block), str(block.false_block), label='False'))
    graph.write_png(files['chart_file'])


