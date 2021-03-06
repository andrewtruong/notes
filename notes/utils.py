# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/06_other/307_utils.ipynb (unless otherwise specified).

__all__ = ['decorate_all_methods_with', 'decorate_function_with', 'coalesce', 'dict_generator', 'DotDict',
           'load_config']

# Cell
def decorate_all_methods_with(decorators):
    '''
    Decorate all methods of a class with a list of decorators
    '''
    if not isinstance(decorators, list):
        decorators = [decorators]

    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                for decorator in decorators:
                    setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate

# Cell
def decorate_function_with(decorators):
    '''
    Apply a list of decorators to a function
    '''
    decorators = decorators if isinstance(decorators, list) else [decorators]

    def decorate(func):
        for decorator in decorators:
            func = decorator(func)
        return func

    return decorate

# Cell
def coalesce(*args, default=None):
    '''
    Provide same function as C# and JS `??` operator
    '''
    return next((a for a in args if a is not None), default)

# Cell
from fastcore.all import typedispatch
from nbdev.showdoc import *

@typedispatch
def func(x:int):
    return x

@typedispatch
def func(x:float):
    return x

show_doc(func)

# Cell
def dict_generator(indict, pre=None):
    '''
    Recursively traverse a dictionary of unknown depth and return flat lists.

    Useful for generating API endpoint strings from JSON-like
    '''
    pre = pre[:] if pre else []
    if isinstance(indict, dict):
        for key, value in indict.items():
            if isinstance(value, dict):
                for d in dict_generator(value, pre + [key]):
                    yield d
            elif isinstance(value, list) or isinstance(value, tuple):
                for v in value:
                    for d in dict_generator(v, pre + [key]):
                        yield d
            else:
                yield pre + [key, value]
    else:
        yield pre + [indict]

# Cell
class DotDict(dict):
    '''
    Dot access that is not perfectly safe, but easier to work with when dealing with nested configs!
    '''
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, d):
        for k, v in d.items():
            if hasattr(v, "keys"):
                v = DotDict(v)
            self[k] = v

# Cell
def load_config(config):
    '''
    Load a yaml config file as a `DotDict`
    '''
    with open(config) as f:
        config = yaml.load(f, yaml.SafeLoader)
        return DotDict(config)