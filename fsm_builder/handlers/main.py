import os

from gi.repository import Gtk
from ..application import chart_file


def main_quit(*args):
    if os.path.isfile(chart_file):
        os.remove(chart_file)
    Gtk.main_quit(*args)


main_handlers = {
    'main_quit': main_quit,
}
