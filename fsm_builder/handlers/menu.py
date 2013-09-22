from gi.repository import Gtk

from ..application import builder, input_alg, draw_chart, chart_file
from ..model.converters import input_to_chart, chart_to_tables


def save_as(parent):

    def add_filters(dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name('Text files')
        filter_text.add_mime_type('text/plain')
        dialog.add_filter(filter_text)

        filter_py = Gtk.FileFilter()
        filter_py.set_name('Python files')
        filter_py.add_mime_type('text/x-python')
        dialog.add_filter(filter_py)

        filter_any = Gtk.FileFilter()
        filter_any.set_name('Any files')
        filter_any.add_pattern('*')
        dialog.add_filter(filter_any)

    dialog = Gtk.FileChooserDialog(
        'Please choose a file', parent, Gtk.FileChooserAction.OPEN,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
         Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

    add_filters(dialog)

    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        print("Open clicked")
        print("File selected: " + dialog.get_filename())
    elif response == Gtk.ResponseType.CANCEL:
        print("Cancel clicked")

    dialog.destroy()


def new(widget):
    input_alg.new()
    input_alg.draw()


def about(aboutdialog):
    aboutdialog.run()
    aboutdialog.hide()


def dict_to_str(dct):
    res = ''
    for fr, tos in dct.items():
        res += '{}: {}\n'.format(fr, ' '.join(map(str, tos)))
    return res


def analize(widget):
    chart = input_to_chart(input_alg)
    draw_chart(chart)
    chart_view = builder.get_object('chart')
    chart_view.set_from_file(chart_file)

    def_table, con_table = chart_to_tables(chart)
    con_table_buffer = builder.get_object('con_table_buffer')
    con_table_buffer.set_text(dict_to_str(con_table))

    def_table_buffer = builder.get_object('def_table_buffer')
    def_table_buffer.set_text(dict_to_str(def_table))


menu_handlers = {
    'menu_save_as': save_as,
    'menu_new': new,
    'menu_about': about,
    'menu_analize': analize,
}
