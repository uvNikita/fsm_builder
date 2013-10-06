import os

from gi.repository import Gtk
from ..application import files


def main_quit(*args):
    if os.path.isfile(files['chart_file']):
        os.remove(files['chart_file'])
    if os.path.isfile(files['graph_file']):
        os.remove(files['graph_file'])
    Gtk.main_quit(*args)


main_handlers = {
    'main_quit': main_quit,
}
