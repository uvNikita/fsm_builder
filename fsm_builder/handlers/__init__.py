from .menu import menu_handlers
from .main import main_handlers
from .toolbar import toolbar_handlers

handlers = {}
handlers.update(menu_handlers)
handlers.update(main_handlers)
handlers.update(toolbar_handlers)


__all__ = ['handlers']

