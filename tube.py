#!/usr/bin/env python3

class Tube():
    def __init__(self, size):
        self.data = list()
        self.capacity = size

    def push(self, obj):
        self.data.append(obj)
        if len(self.data) < self.capacity:
            return None
        return self.data.pop(0)

    def full(self):
        return len(self.data) == self.capacity

    def __iter__(self):
        for i in self.data:
            yield i

    def __getitem__(self, index):
        return self.data[index]

    def __str__(self):
        return str(self.data)

    def __len__(self):
        return len(self.data)
