from functools import wraps

from gi.repository import Gtk

from ..application import id_input, input_alg, id_chooser
from ..model.input import Condition, JumpTo, JumpFrom, Control, End


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
def add_cond(widget, id_):
    input_alg.append(Condition(id_))
    input_alg.draw()


@with_id_chooser
def add_control(widget, id_):
    input_alg.append(Control(id_))
    input_alg.draw()


@with_id_chooser
def add_jump_from(widget, id_):
    input_alg.append(JumpFrom(id_))
    input_alg.draw()


@with_id_chooser
def add_jump_to(widget, id_):
    input_alg.append(JumpTo(id_))
    input_alg.draw()


def add_end(widget):
    input_alg.append(End())
    input_alg.draw()


toolbar_handlers = {
    'add_cond': add_cond,
    'add_control': add_control,
    'add_jump_from': add_jump_from,
    'add_jump_to': add_jump_to,
    'add_end': add_end,
}
