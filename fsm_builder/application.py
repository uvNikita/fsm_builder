import sys
import os

from gi.repository import Gtk

from .model.input import InputAlg

builder = Gtk.Builder()
builder.add_from_file('gui.glade')
module = sys.modules.get('fsm_builder').__file__
gui_file = os.path.join(os.path.dirname(module),
                        os.path.pardir, 'gui.glade')


window = builder.get_object('window')
id_chooser = builder.get_object('id_chooser')
id_input = builder.get_object('id_input')

alg_holder = builder.get_object('alg_label')
input_alg = InputAlg(alg_holder)
