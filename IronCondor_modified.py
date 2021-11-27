from import_bs import blackscholesput, blackscholescall
from numba import jit
from poptions_numba import poptions_numba
import numpy as np
import time


@jit(nopython=True, cache=True)
def bsm_debit(sim_price, strikes, rate, time_fraction, sigma):
    P_short_calls = blackscholescall(sim_price, strikes[0], rate, time_fraction, sigma)
    P_long_calls = blackscholescall(sim_price, strikes[1], rate, time_fraction, sigma)

    P_short_puts = blackscholesput(sim_price, strikes[2], rate, time_fraction, sigma)
    P_long_puts = blackscholesput(sim_price, strikes[3], rate, time_fraction, sigma)

    debit = P_short_calls - P_long_calls + P_short_puts - P_long_puts

    return debit


def ironCondor(nTrials, call_short_strike, call_short_price, call_long_strike, call_long_price,
                    put_short_strike, put_short_price, put_long_strike, put_long_price,
                    underlying, rate, sigma, DTE, fraction, closing_DTE,
                    contracts):

    length = len(closing_DTE)

    # Data Verification
    if call_long_price >= call_short_price:
        return ValueError("Long call price cannot be greater than or "
                                                        "equal to Short call price")

    if call_short_strike >= call_long_strike:
        return ValueError("Short call strike cannot be greater than or "
                                                          "equal to Long call strike")

    if put_long_price >= put_short_price:
        return ValueError("Long put price cannot be greater than or "
                                                       "equal to Short put price")

    if put_short_strike <= put_long_strike:
        return ValueError("Short put strike cannot be less than or "
                                                         "equal to Long put strike")

    if call_short_strike < put_short_strike:
        return ValueError("Short call strike cannot be less than "
                                                          "Short put strike")

    # SIMULATION
    initial_credit = put_short_price - put_long_price + call_short_price - call_long_price
    denom = put_short_strike - put_long_strike
    max_loss = max(put_short_strike - put_long_strike, call_long_strike - call_short_strike) - initial_credit
    # nTrials = 2000

    fraction = [x / 100 for x in fraction]
    min_profit = [initial_credit * x for x in fraction]
    roi = [x / denom * 100 for x in min_profit]
    roi = [round(x, 2) for x in roi]

    strikes = [call_short_strike, call_long_strike, put_short_strike, put_long_strike]

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
