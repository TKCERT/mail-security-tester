import os
import pkgutil
import importlib
from .base import MailTestBase
from .evasion import BaseEvasionFactory

def get_active_classes(base_class):
    """Search package for active classes derived from given base class"""
    path = os.path.dirname(__file__)
    classes = list()
    for finder, name, ispkg in pkgutil.iter_modules([ path ]):
        module = importlib.import_module("." + name, __package__)
        for name, cls in vars(module).items():
            if type(cls) == type and issubclass(cls, base_class) and cls.active:
                classes.append(cls)
    return classes

def get_tests():
    """Return list of active test classes"""
    return get_active_classes(MailTestBase)

def get_evasions():
    """Return list of active evasion classes"""
    return get_active_classes(BaseEvasionFactory)
