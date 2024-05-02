from inspect import getfullargspec, isfunction, getmembers
import importlib.util
import sys
import filters
import img_specifications


def func_without_descr(func):
    def wrapper(*args, **kwargs):
        return func(False, *args, **kwargs)
    return wrapper


def func_descr(func):
    return func(True)


class Func:
    def __init__(self, name, func, descr):
        self.name = name
        self.func = func
        self.description = descr
        self.args = getfullargspec(func).args[1:]

    def print_args(self):
        print(self.args)


def all_func():
    descriptions = dict()
    with open('filters_description.txt') as f:
        for line in f:
            name, descr = line.split(': ')
            descriptions[name] = descr

    res = list()
    for name, func in getmembers(filters, isfunction):
        res.append(Func(name.replace('_', ' '), func, descriptions[name] if name in descriptions else None))

    return res

def all_spec_func(python_file):

    res = list()
    for name, func in getmembers(python_file, isfunction):
        res.append(Func(name.replace('_', ' '), func, None))
    return res


def all_func_from_file(file_path):
    res = list()
    spec = importlib.util.spec_from_file_location("new_filters", file_path)
    new_filters = importlib.util.module_from_spec(spec)
    sys.modules["module.name"] = new_filters
    spec.loader.exec_module(new_filters)
    for name, func in getmembers(new_filters, isfunction):
        res.append(Func(name.replace('_', ' '), func, None))

    return res


class Spec:
    def __init__(self, name, func):
        self.name = name
        self.func = func


def all_spec():
    res = list()
    for name, func in getmembers(img_specifications, isfunction):
        res.append(Spec(name.replace('_', ' '), func))

    return res



if __name__ == '__main__':
    f1 = Func('f1', filters.blur)
    print(f1.description)

