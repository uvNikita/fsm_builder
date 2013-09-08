from gi.repository import Gtk

from ..application import input_alg


def main_quit(*args):
    Gtk.main_quit(*args)


def show_alg_label(label):
    text = ''.join(map(str, input_alg))
    label.set_text('B{}'.format(text))


main_handlers = {
    'main_quit': main_quit,
    'show_alg_label': show_alg_label,
}
