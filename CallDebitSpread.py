from numba import jit
from poptions_numba import poptions_numba
import time
from import_bs import blackscholescall
import numpy as np


@jit(nopython=True, cache=True)
def bsm_debit(sim_price, strikes, rate, time_fraction, sigma):
    P_short_calls = blackscholescall(sim_price, strikes[0], rate, time_fraction, sigma)
    P_long_calls = blackscholescall(sim_price, strikes[1], rate, time_fraction, sigma)

    credit = P_long_calls - P_short_calls
    debit = -credit

    return debit


def callDebitSpread(trials, short_strike, short_price, long_strike, long_price,
                    underlying, rate, sigma, DTE, fraction, closing_DTE):

    # Data Verification
    if long_price <= short_price:
        return ValueError("Long price cannot be less than or equal to Short price")

    if short_strike <= long_strike:
        return ValueError("Short strike cannot be less than or equal to Long strike")

    # SIMULATION
    initial_debit = long_price - short_price  # Debit paid from opening trade
    initial_credit = -1 * initial_debit

    fraction = [x / 100 for x in fraction]
    max_profit = short_strike - long_strike - initial_debit
    min_profit = [max_profit * x for x in fraction]

    strikes = [short_strike, long_strike]

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
