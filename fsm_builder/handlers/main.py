import os

from gi.repository import Gtk
from ..application import files


def main_quit(*args):
    if os.path.isfile(files['chart_file']):
        os.remove(files['chart_file'])
    Gtk.main_quit(*args)


main_handlers = {
    'main_quit': main_quit,
}
