from functools import wraps

from gi.repository import Gtk

from ..application import input_alg, builder
from ..model.input import Condition, JumpTo, JumpFrom, Control, End, ControlBlock


id_chooser = builder.get_object('id_chooser')
id_input = builder.get_object('id_input')

control_dialog = builder.get_object('control_dialog')
control_input = builder.get_object('control_input')


def with_indexchooser(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        response = id_chooser.run()
        if response:
            index = id_input.get_value_as_int()
            kwargs.update(index=index)
            handler(*args, **kwargs)
        id_input.set_value(0)
        id_chooser.hide()
    return wrapper


@with_indexchooser
def add_cond(widget, index):
    input_alg.insert(Condition(index))
    input_alg.draw()


def add_control(widget):
    response = control_dialog.run()
    try:
        if response:
            ids = control_input.get_text().split(' ')
            ids = list(map(int, ids))
            if len(ids) == 1:
                input_alg.insert(Control(ids[0]))
            else:
                input_alg.insert(ControlBlock(ids))
    except ValueError as e:
        print(e)
    finally:
        control_input.set_text('')
        control_dialog.hide()
        input_alg.draw()


@with_indexchooser
def add_jump_from(widget, index):
    input_alg.insert(JumpFrom(index))
    input_alg.draw()


@with_indexchooser
def add_jump_to(widget, index):
    input_alg.insert(JumpTo(index))
    input_alg.draw()


def add_end(widget):
    input_alg.insert(End())
    input_alg.draw()


def delete(widget):
    input_alg.delete()
    input_alg.draw()


def move_left(widget):
    input_alg.move_left()
    input_alg.draw()


def move_right(widget):
    input_alg.move_right()
    input_alg.draw()


toolbar_handlers = {
    'add_cond': add_cond,
    'add_control': add_control,
    'add_jump_from': add_jump_from,
    'add_jump_to': add_jump_to,
    'add_end': add_end,
    'move_left': move_left,
    'move_right': move_right,
    'delete': delete,
}
