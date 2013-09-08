#!/usr/bin/python

from gi.repository import Gtk

from fsm_builder.application import builder, window
from fsm_builder.handlers import handlers


if __name__ == '__main__':
    builder.connect_signals(handlers)
    window.show_all()
    Gtk.main()
