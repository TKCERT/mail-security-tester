import os
import pkgutil
import importlib
from .base import MailTestBase

def getTests():
    """Return list of test classes"""
    path = os.path.dirname(__file__)
    test_classes = list()
    for finder, name, ispkg in pkgutil.iter_modules([ path ]):
        module = importlib.import_module("." + name, __package__)
        for name, cls in vars(module).items():
            if type(cls) == type and issubclass(cls, MailTestBase) and cls.active:
                test_classes.append(cls)
    return test_classes
