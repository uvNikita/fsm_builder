from gi.repository import Gtk


def main_quit(*args):
    Gtk.main_quit(*args)


main_handlers = {
    'main_quit': main_quit,
}
