from functools import wraps

from gi.repository import Gtk

from ..application import id_input, input_alg, id_chooser
from ..model.input import Condition, JumpTo, JumpFrom, Node, End


def with_id_chooser(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        response = id_chooser.run()
        if response:
            id_ = id_input.get_value_as_int()
            kwargs.update(id_=id_)
            handler(*args, **kwargs)
        id_input.set_value(0)
        id_chooser.hide()
    return wrapper


@with_id_chooser
def add_cond(dest, id_):
    input_alg.append(Condition(id_))
    dest.emit('show')


@with_id_chooser
def add_node(dest, id_):
    input_alg.append(Node(id_))
    dest.emit('show')


@with_id_chooser
def add_jump_from(dest, id_):
    input_alg.append(JumpFrom(id_))
    dest.emit('show')


@with_id_chooser
def add_jump_to(dest, id_):
    input_alg.append(JumpTo(id_))
    dest.emit('show')


def add_end(dest):
    input_alg.append(End())
    dest.emit('show')


toolbar_handlers = {
    'add_cond': add_cond,
    'add_node': add_node,
    'add_jump_from': add_jump_from,
    'add_jump_to': add_jump_to,
    'add_end': add_end,
}
