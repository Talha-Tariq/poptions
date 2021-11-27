from numba import jit
from poptions_numba import poptions_numba
import time
from import_bs import blackscholescall
import numpy as np
import math


@jit(nopython=True, cache=True)
def bsm_debit(sim_price, strikes, rate, time_fraction, sigma):
    P_long_calls = blackscholescall(sim_price, strikes[0], rate, time_fraction, sigma)

    credit = P_long_calls
    debit = -credit

    return debit


def longCall(nTrials, long_strike, long_price,
                     underlying, rate, sigma, DTE, fraction, closing_DTE, contracts):

    length = len(closing_DTE)

    # SIMULATION
    initial_debit = long_price  # Debit paid from opening trade
    initial_credit = -1 * initial_debit
    denom = 0  # Buying Power Reduction (NO MARGIN FOR BUYING LONG OPTIONS!)
    max_loss = initial_debit
    # nTrials = 2000

    # fraction = [x / 100 for x in fraction] # Fraction is now pseudo-multiplier of debit paid
    max_profit = math.inf
    min_profit = [initial_debit * x for x in fraction]
    roi = [x / initial_debit * 100 for x in min_profit]
    roi = [round(x, 2) for x in roi]

    strikes = [long_strike]

    # LISTS TO NUMPY ARRAYS CUZ NUMBA HATES LISTS
    strikes = np.array(strikes)
    closing_DTE = np.array(closing_DTE)
    min_profit = np.array(min_profit)
    roi = np.array(roi)

    # start_numba = time.perf_counter()

    try:
        pop, pop_error, avg_dte, avg_dte_err = poptions_numba(underlying, rate, sigma, DTE, closing_DTE, nTrials,
                                                              initial_credit, denom,
                                                              max_loss, min_profit, roi, strikes, contracts, length,
                                                              bsm_debit)
    except RuntimeError as err:
        print(err.args)

    # end_numba = time.perf_counter()

    # print("Time taken for Numba WITH COMPILATION: {}".format(end_numba - start_numba))

    # print("ROI")
    # print(roi)

    # min_profit = [x * 100 * contracts for x in min_profit]
    # min_profit = [round(x, 2) for x in min_profit]

    # print("Max Profit w/ fraction:")
    # print(min_profit)

    # print('Credit Received/Debit Paid : $ %.2f \n' % (initial_credit * 100 * contracts))
    # print('Buying Power Reduction : $ %.2f \n' % (denom * 100 * contracts))
    # print('Max Loss : $ %.2f \n' % (max_loss * 100 * contracts))

    response = {
        "pop": pop,
        "pop_error": pop_error,
        "avg_days": avg_dte,
        "avg_days_err": avg_dte_err
    }

    return response