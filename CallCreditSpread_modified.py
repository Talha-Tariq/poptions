from numba import jit
from poptions_numba import poptions_numba
import time
from import_bs import blackscholescall
import numpy as np


# changes:
# moved length to monte

@jit(nopython=True, cache=True)
def bsm_debit(sim_price, strikes, rate, time_fraction, sigma):
    P_short_calls = blackscholescall(sim_price, strikes[0], rate, time_fraction, sigma)
    P_long_calls = blackscholescall(sim_price, strikes[1], rate, time_fraction, sigma)

    debit = P_short_calls - P_long_calls

    return debit


def callCreditSpread(nTrials, short_strike, short_price, long_strike, long_price,
                     underlying, rate, sigma, DTE, fraction, closing_DTE, contracts):

    # Data Verification
    if long_price >= short_price:
        raise ValueError("Long price cannot be greater than or equal to Short price")

    if short_strike >= long_strike:
        raise ValueError("Short strike cannot be greater than or equal to Long strike")

    # SIMULATION
    initial_credit = short_price - long_price  # Credit received from opening trade
    denom = long_strike - short_strike  # Buying Power Reduction
    max_loss = denom - initial_credit

    fraction = [x / 100 for x in fraction]
    min_profit = [initial_credit * x for x in fraction]
    roi = [x / denom * 100 for x in min_profit]
    roi = [round(x, 2) for x in roi]

    strikes = [short_strike, long_strike]

    # LISTS TO NUMPY ARRAYS CUZ NUMBA HATES LISTS
    strikes = np.array(strikes)
    closing_DTE = np.array(closing_DTE)
    min_profit = np.array(min_profit)
    roi = np.array(roi)

    # start_numba = time.perf_counter()

    try:
        pop, pop_error, avg_dte, avg_dte_err = poptions_numba(underlying, rate, sigma, DTE, closing_DTE, nTrials,
                                                              initial_credit, denom,
                                                              max_loss, min_profit, roi, strikes, contracts,
                                                              bsm_debit)
    except RuntimeError as err:
        print(err.args)

    # end_numba = time.perf_counter()

    # print("Time taken for Numba WITH COMPILATION: {}".format(end_numba - start_numba))\

    response = {
        "pop": pop,
        "pop_error": pop_error,
        "avg_days": avg_dte,
        "avg_days_err": avg_dte_err
    }

    return response
