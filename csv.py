#!/usr/bin/env python3


class CSV(object):
    def __init__(self, obj=None):
        self.c = dict()
        content = ''
        if obj is None:
            return
        if isinstance(obj, str):
            content = obj
        else:
            try:
                content = obj.read()
                lines = content.splitlines()
                head = lines[0].split(',')
                for item in head:
                    key = item.lstrip().rstrip()
                    if not key:
                        continue
                    if key not in self.c.keys():
                        self.c[key] = list()
                for line in lines[1:]:
                    elements = line.split(',')
                    for i in range(len(head)):
                        if i >= len(elements):
                            self.c[head[i]].append(0.0)
                        else:
                            self.c[head[i]].append(
                                float(elements[i].lstrip().rstrip())
                            )
            except AttributeError:
                return

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.c[key]
        elif isinstance(key, int):
            line = dict()
            index = key
            for k in self.c.keys():
                line[k] = self.c[k][index]
            return line
        else:
            raise TypeError('Getter accepts only string or integer')

    def __iter__(self):
        i = 0
        while True:
            line = dict()
            for key in self.c.keys():
                if i >= len(self.c[key]):
                    raise StopIteration()
                line[key] = self.c[key][i]
            yield line
            i += 1

    def __str__(self):
        text = ','.join(self.c.keys()) + '\n'
        for line in self:
            text += ','.join([str(val) for val in line.values()])
            text += '\n'
        return text

    def __len__(self):
        if len(self.c.keys()) == 0:
            return 0
        return list(self.c.values())[0].__len__()

    def keys(self):
        return list(self.c.keys())

    def setcell(self, a, b, value):
        if isinstance(a, int) and isinstance(b, str):
            self.c[b][a] = float(value)
        elif isinstance(a, str) and isinstance(b, int):
            self.c[a][b] = float(value)
        else:
            raise TypeError('Requires a string for key and a int for index.')

    def addline(self, elements):
        if not len(self.c.keys()) == len(elements):
            raise TypeError('Number of elements is not consistent with that of table keys')
        if isinstance(elements, dict):
            if not elements.keys() == self.c.keys():
                raise TypeError('Keys are inconsistent')
            for k in elements.keys():
                self.c[k].append(elements[k])
        else:
            keys = list(self.c.keys())
            for i in range(len(keys)):
                self.c[keys[i]].append(elements[i])

    def addcol(self, key, default=0.0):
        length = list(self.c.values())[0].__len__() if self.c.keys() else 0
        self.c[key] = list()
        for i in range(length):
            self.c[key].append(default)

    def popcol(self, key):
        del self.c[key]

    def popline(self, index):
        for col in self.c.values():
            del col[index]
