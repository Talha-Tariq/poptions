from numba import jit
from math import log, sqrt, exp, erf


@jit(nopython=True, cache=True)
def blackscholesput(s, k, rr, tt, sd):
    if tt == 0 and (s / k > 1):
        p = 0
    elif tt == 0 and (s / k < 1):
        p = k - s
    elif tt == 0 and (s / k == 1):
        p = 0
    else:
        d1 = (log(s / k) + (rr + (1 / 2) * sd ** 2) * tt) / (sd * sqrt(tt))  # 80 ms
        d2 = d1 - sd * sqrt(tt)  # 20 ms
        c = s * ((1.0 + erf(d1 / sqrt(2.0))) / 2.0) - k * exp(-rr * tt) * ((1.0 + erf(d2 / sqrt(2.0))) / 2.0)   # 130 ms
        # c = s * norm_cum_dist(d1) - k * exp(-rr * tt) * norm_cum_dist(d2) # 130 ms
        p = k * exp(-rr * tt) - s + c  # 30 ms

    return p


@jit(nopython=True, cache=True)
def blackscholescall(s, k, rr, tt, sd):
    if tt == 0 and (s / k > 1):
        c = s - k
    elif tt == 0 and (s / k < 1):
        c = 0
    elif tt == 0 and (s / k == 1):
        c = 0
    else:
        d1 = (log(s / k) + (rr + (1 / 2) * sd ** 2) * tt) / (sd * sqrt(tt))  # 80 ms
        d2 = d1 - sd * sqrt(tt)  # 20 ms
        c = s * ((1.0 + erf(d1 / sqrt(2.0))) / 2.0) - k * exp(-rr * tt) * ((1.0 + erf(d2 / sqrt(2.0))) / 2.0)  # 130 ms
        # c = s * norm_cum_dist(d1) - k * exp(-rr * tt) * norm_cum_dist(d2)  # 130 ms

    return c


# @jit(nopython=True, cache=True)
# def norm_cum_dist(x):
#     # 'Cumulative distribution function for the standard normal distribution'
#     # return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
#     return (1.0 + erf(x / sqrt(2.0))) / 2.0