from numba import jit
from math import log, sqrt, exp, erf


def blackScholesPut(s, k, rr, tt, sd):
    if tt == 0 and (s / k > 1):
        p = 0
    elif tt == 0 and (s / k < 1):
        p = k - s
    elif tt == 0 and (s / k == 1):
        p = 0
    else:
        d1 = (log(s / k) + (rr + (1 / 2) * sd ** 2) * tt) / (sd * sqrt(tt))
        d2 = d1 - sd * sqrt(tt)
        c = s * ((1.0 + erf(d1 / sqrt(2.0))) / 2.0) - k * exp(-rr * tt) * ((1.0 + erf(d2 / sqrt(2.0))) / 2.0)
        p = k * exp(-rr * tt) - s + c

    return p


def blackScholesCall(s, k, rr, tt, sd):
    if tt == 0 and (s / k > 1):
        c = s - k
    elif tt == 0 and (s / k < 1):
        c = 0
    elif tt == 0 and (s / k == 1):
        c = 0
    else:
        d1 = (log(s / k) + (rr + (1 / 2) * sd ** 2) * tt) / (sd * sqrt(tt))
        d2 = d1 - sd * sqrt(tt)
        c = s * ((1.0 + erf(d1 / sqrt(2.0))) / 2.0) - k * exp(-rr * tt) * ((1.0 + erf(d2 / sqrt(2.0))) / 2.0)

    return c
