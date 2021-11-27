from numba import jit
from poptions_numba import poptions_numba
import time
from import_bs import blackscholesput
import numpy as np


@jit(nopython=True, cache=True)
def bsm_debit(sim_price, strikes, rate, time_fraction, sigma):
    P_short_puts = blackscholesput(sim_price, strikes[0], rate, time_fraction, sigma)
    P_long_puts = blackscholesput(sim_price, strikes[1], rate, time_fraction, sigma)

    debit = P_short_puts - P_long_puts

    return debit


def putCreditSpread(nTrials, short_strike, short_price, long_strike, long_price,
                     underlying, rate, sigma, DTE, fraction, closing_DTE, contracts):

    length = len(closing_DTE)

    # Data Verification
    if long_price >= short_price:
        return ValueError("Long price cannot be greater than or equal to Short price")

    if short_strike <= long_strike:
        return ValueError("Short strike cannot be less than or equal to Long strike")

    # SIMULATION
    initial_credit = short_price - long_price  # Credit received from opening trade
    denom = short_strike - long_strike  # Buying Power Reduction
    max_loss = denom - initial_credit
    # nTrials = 2000

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
