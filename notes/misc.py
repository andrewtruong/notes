# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/06_other/300_misc.ipynb (unless otherwise specified).

__all__ = ['flatten', 'DotDict', 'suppress_stdout', 'Show', 'coalesce', 'show_plotly', 'Hook', 'HookBwd',
           'decorate_all_methods_with', 'decorate_function_with', 'dict_generator']

# Cell
import itertools
from fastcore.all import typedispatch, patch
from fastai.vision.all import *
from collections.abc import Iterable
from IPython.display import HTML
from contextlib import contextmanager
from pathlib import Path

# Cell
@typedispatch
def chunks(lst:list, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

@typedispatch
def chunks(iterable:Iterable, n):
    """
    Modified for convenience from: https://stackoverflow.com/a/8998040
    """
    it = iter(iterable)
    while True:
        chunk_it = itertools.islice(it, n)
        try:
            first_el = next(chunk_it)
        except StopIteration:
            return
        yield itertools.chain((first_el,), chunk_it)

# show_doc(chunks)

# Cell
def flatten(iterable:Iterable):
    '''
    From: https://stackoverflow.com/a/2158532
    '''
    for el in iterable:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el

# Cell
class DotDict(dict):
    "Enable dot access to a dictionary.  e.g. `dict.key1.key2.key3`"
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct):
        for key, value in dct.items():
            if hasattr(value, 'keys'):
                value = DotDict(value)
            self[key] = value

# Cell
@contextmanager
def suppress_stdout():
    '''
    Suppress any stdout in this `with` block
    '''
    initial_stdout = sys.stdout
    try:
        with open('/dev/null', 'w') as f:
            sys.stdout = f
            yield
    finally:
        sys.stdout = initial_stdout

# Cell
class Show:
    "Show multiple HTML reprs in the same cell"
    template = """<div style="float: left; padding: 10px;">
    <p style='font-family:"Arial"'>{0}</p>{1}
    </div>"""

    def __init__(self, things:dict):
        self.things = things

    def _repr_html_(self):
        return '\n'.join(self.template.format(name, data._repr_html_()) for name, data in self.things.items())

    def __repr__(self):
        return '\n\n'.join(name + '\n' + repr(data) for name, data in self.things.items())

# Cell
def coalesce(*args, default=None):
    '''
    Provide same function as C# and JS `??` operator
    '''
    return next((a for a in args if a is not None), default)

# Cell
def show_plotly(fig):
    '''
    Render plotly figs with nbdev
    '''
    return HTML(fig.to_html(config={'displayModeBar': False}))

# Cell
class Hook():
    def __init__(self, m):
        self.hook = m.register_forward_hook(self.hook_func)
    def hook_func(self, m, i, o): self.stored = o.detach().clone()
    def __enter__(self, *args): return self
    def __exit__(self, *args): self.hook.remove()

# Cell
class HookBwd():
    def __init__(self, m):
        self.hook = m.register_backward_hook(self.hook_func)
    def hook_func(self, m, gi, go): self.stored = go[0].detach().clone()
    def __enter__(self, *args): return self
    def __exit__(self, *args): self.hook.remove()

# Cell
@patch
def show_activations(self: Learner, img):
    img = Path(img)
    pipeline = Pipeline([PILImage.create, ToTensor, Resize(224, method='squish'), IntToFloatTensor])
    x = pipeline(img).unsqueeze(0)
    y, name = img.parent.name.split('-')
    y = int(y)

    with HookBwd(learner.model.body) as hookg:
        with Hook(learner.model.body) as hook:
            output = learner.model.eval()(x)
            act = hook.stored
        output[0,y].backward()
        grad = hookg.stored


    w = grad[0].mean(dim=[1,2], keepdim=True)
    cam_map = (w * act[0]).sum(0)

    _,ax = plt.subplots()
    x[0].show(ctx=ax)
    ax.title.set_text(name)
    ax.imshow(cam_map.detach().cpu(), alpha=0.80, extent=(0,224,224,0),
                  interpolation='sinc', cmap='magma_r')

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