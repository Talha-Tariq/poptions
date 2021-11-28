from numba import jit
from poptions_numba import poptions_numba
import time
from import_bs import blackscholescall
import numpy as np


@jit(nopython=True, cache=True)
def bsm_debit(sim_price, strikes, rate, time_fraction, sigma):
    P_short_calls = blackscholescall(sim_price, strikes[0], rate, time_fraction, sigma)

    debit = P_short_calls
    credit = sim_price
    debit = debit - credit

    return debit


def coveredCall(trials, short_strike, short_price,
                underlying, rate, sigma, DTE, fraction, closing_DTE):

    # SIMULATION
    initial_credit = short_price  # Credit received from opening trade
    stock_debit = underlying  # Assuming current underlying price = purchase price
    initial_credit = initial_credit - stock_debit

    fraction = [x / 100 for x in fraction]
    max_profit = short_price + (short_strike - underlying)
    min_profit = [max_profit * x for x in fraction]

    strikes = [short_strike]

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