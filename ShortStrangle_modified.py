from numba import jit
from poptions_numba import poptions_numba
import time
from import_bs import blackscholescall, blackscholesput
import numpy as np
import math


@jit(nopython=True, cache=True)
def bsm_debit(sim_price, strikes, rate, time_fraction, sigma):
    P_short_calls = blackscholescall(sim_price, strikes[0], rate, time_fraction, sigma)
    P_short_puts = blackscholesput(sim_price, strikes[1], rate, time_fraction, sigma)

    debit = P_short_calls + P_short_puts

    return debit


def shortStrangle(nTrials, call_strike, call_price, put_strike, put_price,
                     underlying, rate, sigma, DTE, fraction, closing_DTE, contracts):

    length = len(closing_DTE)

    # Data Verification
    if call_strike < put_strike:
        return ValueError("Call Strike cannot be less than Put Strike")

    # SIMULATION
    initial_credit = call_price + put_price  # Credit received from opening trade

    bpr_put = put_price + max(0.2 * underlying - (underlying - put_strike), 0.1 * put_strike)
    bpr_call = call_price + max(0.2 * underlying - (call_strike - underlying), 0.1 * underlying)

    if bpr_put > bpr_call:
        denom = bpr_put + call_price
    else:
        denom = bpr_call + put_price

    max_loss = math.inf
    # nTrials = 2000

    fraction = [x / 100 for x in fraction]
    min_profit = [initial_credit * x for x in fraction]
    roi = [x / denom * 100 for x in min_profit]
    roi = [round(x, 2) for x in roi]

    strikes = [call_strike, put_strike]

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