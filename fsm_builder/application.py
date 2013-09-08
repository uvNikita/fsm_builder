import sys
import os

from gi.repository import Gtk

from .model.input import InputAlg

builder = Gtk.Builder()
module = sys.modules.get('fsm_builder').__file__
gui_file = os.path.join(os.path.dirname(module),
                        os.path.pardir, 'gui.glade')
builder.add_from_file(gui_file)

alg_holder = builder.get_object('alg_label')
input_alg = InputAlg(alg_holder)
