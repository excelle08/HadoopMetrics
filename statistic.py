#!/usr/bin/env python3
from is_close import isclose
import math

def compute_rel(x, y, strict=False):
    if len(x) != len(y):
        raise ArithmeticError('X and Y should have same length.')
    x_bar = 0; y_bar = 0; n = len(x)
    cov_xy = 0
    div_x = 0; div_y = 0
    if n <= 1:
        if not strict:
            return 0, y[0], 1, 2
        else:
            raise ArithmeticError('Insufficient Samples')
    for i in range(n):
        x_bar += x[i] / n
        y_bar += y[i] / n
    for i in range(n):
        div_x += (x[i] - x_bar) ** 2
        div_y += (y[i] - y_bar) ** 2
        cov_xy += (x[i] - x_bar) * (y[i] - y_bar)
    div_x /= n
    div_y /= n
    cov_xy /= n

    if isclose(div_x, 0.0) or isclose(div_y, 0.0):
        if not strict:
            return 0, y[0], 0, len(x)
        else:
            raise ArithmeticError('Variance is Zero')
    b = cov_xy / div_x
    a = y_bar - b * x_bar
    r = cov_xy / (math.sqrt(div_x) * math.sqrt(div_y))
    return b, a, r, n
