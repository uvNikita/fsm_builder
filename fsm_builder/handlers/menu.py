import pickle
from functools import wraps

from gi.repository import Gtk

from ..application import builder, input_alg, draw_chart, files, fsm_graph, trans_table
from ..model.chart import get_paths
from ..model.converters import input_to_chart, chart_to_tables, ParseError
from ..model.converters import chart_to_graph, graph_to_trans_table
from .util import get_handler_constructor


menu_handlers = {}
handler = get_handler_constructor(menu_handlers)


def with_file_dialog(action):

    def add_filters(dialog):
        filter_fsm = Gtk.FileFilter()
        filter_fsm.set_name('FSM Builder data file')
        filter_fsm.add_mime_type('application/octet-stream')
        dialog.add_filter(filter_fsm)

        filter_graph = Gtk.FileFilter()
        filter_graph.set_name('FSM Builder graph file')
        filter_graph.add_mime_type('text/plain')
        dialog.add_filter(filter_graph)

        filter_any = Gtk.FileFilter()
        filter_any.set_name('Any files')
        filter_any.add_pattern('*')
        dialog.add_filter(filter_any)

    def decorator(func):
        @wraps(func)
        def wraper(*args, **kwargs):
            parent = builder.get_object('window')
            if action == 'save':
                dialog = Gtk.FileChooserDialog(
                    'Please choose a file to save', parent, Gtk.FileChooserAction.SAVE,
                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                     Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
            else:
                dialog = Gtk.FileChooserDialog(
                    'Please choose a file to open', parent, Gtk.FileChooserAction.OPEN,
                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                     Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
            add_filters(dialog)

            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                path = dialog.get_filename()
                func(path)
            dialog.destroy()
        return wraper
    return decorator




@handler('menu_save_as')
@with_file_dialog('save')
def save_as(path):
    if not path.endswith('.fsmd'):
        path += '.fsmd'
    with open(path, 'wb') as f:
        pickle.dump(input_alg.alg, f)
        files['data_file'] = path


@handler('menu_save')
def save(widget):
    if files['data_file'] is None:
        return save_as(widget)
    else:
        with open(files['data_file'], 'wb') as f:
            pickle.dump(input_alg.alg, f)


@handler('menu_open')
@with_file_dialog('open')
def open_file(path):
    with open(path, 'rb') as f:
        loaded_alg = pickle.load(f)
        files['data_file'] = path
    input_alg.load_alg(loaded_alg)
    input_alg.draw()


@handler('menu_new')
def new(widget):
    input_alg.new()
    input_alg.draw()
    trans_table.draw()


@handler('menu_about')
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


@handler('menu_analyze')
def analyze(widget):
    statusbar = builder.get_object('statusbar')
    try:
        chart = input_to_chart(input_alg)
    except ParseError as e:
        input_alg.draw(errors=[e.idx])
        statusbar.push(1, str(e))
        return
    statusbar.remove_all(1)

    graph = chart_to_graph(chart)
    nodes, conns = graph

    draw_chart(chart, nodes)
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

    fsm_graph.fill(nodes.values(), conns)
    fsm_graph.put_codes()
    fsm_graph.draw()

    table = graph_to_trans_table((fsm_graph.nodes, fsm_graph.connections))
    trans_table.fill(table)
    trans_table.draw()


@handler('menu_export_graph')
@with_file_dialog('save')
def export_graph(path):
    if not path.endswith('.fsmg'):
        path += '.fsmg'
    with open(path, 'w') as f:
        fsm_graph.dump(f)


@handler('menu_import_graph')
@with_file_dialog('open')
def import_graph(path):
    with open(path) as f:
        fsm_graph.load(f)
    fsm_graph.draw()

