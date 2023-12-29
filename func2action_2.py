from inspect import getfullargspec, isfunction, getmembers



class Func:
    def __init__(self, name, func):
        self.name = name
        self.func = func
        self.args = getfullargspec(func).args[1:]

    def print_args(self):
        print(self.args)


def all_func(module):
    res = list()
    for name, func in getmembers(module, isfunction):
        res.append(Func(name, func))

    return res


if __name__ == '__main__':
    import filters
    print(getmembers(filters, isfunction))
