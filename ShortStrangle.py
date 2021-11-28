from numba import jit
from poptions_numba import poptions_numba
import time
from import_bs import blackscholescall, blackscholesput
import numpy as np


@jit(nopython=True, cache=True)
def bsm_debit(sim_price, strikes, rate, time_fraction, sigma):
    P_short_calls = blackscholescall(sim_price, strikes[0], rate, time_fraction, sigma)
    P_short_puts = blackscholesput(sim_price, strikes[1], rate, time_fraction, sigma)

    debit = P_short_calls + P_short_puts

    return debit


def shortStrangle(trials, call_strike, call_price, put_strike, put_price,
                  underlying, rate, sigma, DTE, fraction, closing_DTE):

    # Data Verification
    if call_strike < put_strike:
        return ValueError("Call Strike cannot be less than Put Strike")

    # SIMULATION
    initial_credit = call_price + put_price  # Credit received from opening trade

    fraction = [x / 100 for x in fraction]
    min_profit = [initial_credit * x for x in fraction]

    strikes = [call_strike, put_strike]

    # LISTS TO NUMPY ARRAYS CUZ NUMBA HATES LISTS
    strikes = np.array(strikes)
    closing_DTE = np.array(closing_DTE)
    min_profit = np.array(min_profit)

    # start_numba = time.perf_counter()

    try:
        pop, pop_error, avg_dte, avg_dte_err = poptions_numba(underlying, rate, sigma, DTE, closing_DTE, trials,
                                                              initial_credit, min_profit, strikes, bsm_debit)
    except RuntimeError as err:
        print(err.args)

    # end_numba = time.perf_counter()

    # print("Time taken for Numba WITH COMPILATION: {}".format(end_numba - start_numba))

    response = {
        "pop": pop,
        "pop_error": pop_error,
        "avg_days": avg_dte,
        "avg_days_err": avg_dte_err
    }

    return response