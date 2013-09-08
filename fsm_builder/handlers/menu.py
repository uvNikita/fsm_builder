from gi.repository import Gtk

from ..application import window


def save_as(widget):

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
        'Please choose a file', window, Gtk.FileChooserAction.OPEN,
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


menu_handlers = {
    'save_as': save_as
}
