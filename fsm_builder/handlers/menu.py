import pickle
from gi.repository import Gtk

from ..application import builder, input_alg, draw_chart, files
from ..model.chart import get_paths
from ..model.converters import input_to_chart, chart_to_tables, ParseError


def add_filters(dialog):
    filter_text = Gtk.FileFilter()
    filter_text.set_name('FSM Builder files')
    filter_text.add_mime_type('application/octet-stream')
    dialog.add_filter(filter_text)

    filter_any = Gtk.FileFilter()
    filter_any.set_name('Any files')
    filter_any.add_pattern('*')
    dialog.add_filter(filter_any)


def save_as(widget):
    parent = builder.get_object('window')
    dialog = Gtk.FileChooserDialog(
        'Please choose a file to save', parent, Gtk.FileChooserAction.SAVE,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
         Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

    add_filters(dialog)

    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        path = dialog.get_filename()
        if not path.endswith('.fsmd'):
            path += '.fsmd'
        with open(path, 'wb') as f:
            pickle.dump(input_alg.alg, f)
            files['data_file'] = path
    dialog.destroy()


def save(widget):
    print(files['data_file'])
    if files['data_file'] is None:
        return save_as(widget)
    else:
        with open(files['data_file'], 'wb') as f:
            pickle.dump(input_alg.alg, f)


def open_file(widget):
    parent = builder.get_object('window')
    dialog = Gtk.FileChooserDialog(
        'Please choose a file to save', parent, Gtk.FileChooserAction.OPEN,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
         Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    add_filters(dialog)

    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        path = dialog.get_filename()
        with open(path, 'rb') as f:
            loaded_alg = pickle.load(f)
            files['data_file'] = path
        input_alg.load_alg(loaded_alg)
        input_alg.draw()
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


def list_to_str(lst):
    res = '    '
    res += ' '.join(map(str, range(len(lst))))
    res += '\n'
    for idx, row in enumerate(lst):
        row = ' '.join(map(str, row))
        res += '{idx}: {row}\n'.format(idx=idx, row=row)
    return res


def paths_to_str(paths):
    res = ''
    for path in paths:
        res += ' -> '.join(map(str, path))
        res += '\n'
    return res


def analyze(widget):
    statusbar = builder.get_object('statusbar')
    try:
        chart = input_to_chart(input_alg)
    except ParseError as e:
        input_alg.draw(errors=[e.idx])
        statusbar.push(1, str(e))
        return
    statusbar.remove_all(1)
    draw_chart(chart)
    chart_view = builder.get_object('chart')
    chart_view.set_from_file(files['chart_file'])

    def_table, con_table = chart_to_tables(chart)
    con_table_buffer = builder.get_object('con_table_buffer')
    con_table_buffer.set_text(list_to_str(con_table))

    def_table_buffer = builder.get_object('def_table_buffer')
    def_table_buffer.set_text(dict_to_str(def_table))

    paths, loops = get_paths(chart)
    paths_buffer = builder.get_object('paths_buffer')
    paths_buffer.set_text(paths_to_str(paths))
    loops_buffer = builder.get_object('loops_buffer')
    loops_buffer.set_text(paths_to_str(loops))


menu_handlers = {
    'menu_save_as': save_as,
    'menu_save': save,
    'menu_open': open_file,
    'menu_new': new,
    'menu_about': about,
    'menu_analyze': analyze,
}
