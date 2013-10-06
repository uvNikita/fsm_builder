import os

from gi.repository import Gtk
from ..application import files
from .util import get_handler_constructor


main_handlers = {}


handler = get_handler_constructor(main_handlers)


@handler('main_quit')
def main_quit(*args):
    if os.path.isfile(files['chart_file']):
        os.remove(files['chart_file'])
    if os.path.isfile(files['graph_file']):
        os.remove(files['graph_file'])
    Gtk.main_quit(*args)
