from BlackScholes import blackScholesPut, blackScholesCall
from numba import jit
from MonteCarlo import monteCarlo
import numpy as np
import time


def bsm_debit(sim_price, strikes, rate, time_fraction, sigma):
    P_short_calls = blackScholesCall(sim_price, strikes[0], rate, time_fraction, sigma)
    P_long_calls = blackScholesCall(sim_price, strikes[1], rate, time_fraction, sigma)

    P_short_puts = blackScholesPut(sim_price, strikes[2], rate, time_fraction, sigma)
    P_long_puts = blackScholesPut(sim_price, strikes[3], rate, time_fraction, sigma)

    debit = P_short_calls - P_long_calls + P_short_puts - P_long_puts

    return debit


def ironCondor(underlying, sigma, rate, trials, days_to_expiration,
               closing_days_array, percentage_array, put_short_strike,
               put_short_price, put_long_strike, put_long_price, call_short_strike,
               call_short_price, call_long_strike, call_long_price):

    # Data Verification
    if call_long_price >= call_short_price:
        raise ValueError("Long call price cannot be greater than or "
                                                        "equal to Short call price")

    if call_short_strike >= call_long_strike:
        raise ValueError("Short call strike cannot be greater than or "
                                                          "equal to Long call strike")

    if put_long_price >= put_short_price:
        raise ValueError("Long put price cannot be greater than or "
                                                       "equal to Short put price")

    if put_short_strike <= put_long_strike:
        raise ValueError("Short put strike cannot be less than or "
                                                         "equal to Long put strike")

    if call_short_strike < put_short_strike:
        raise ValueError("Short call strike cannot be less than "
                                                          "Short put strike")

    for closing_days in closing_days_array:
        if closing_days > days_to_expiration:
            raise ValueError("Closing days cannot be beyond Days To Expiration.")

    if len(closing_days_array) != len(percentage_array):
        raise ValueError("closing_days_array and percentage_array sizes must be equal.")

    # SIMULATION
    initial_credit = put_short_price - put_long_price + call_short_price - call_long_price

    percentage_array = [x / 100 for x in percentage_array]
    min_profit = [initial_credit * x for x in percentage_array]

    strikes = [call_short_strike, call_long_strike, put_short_strike, put_long_strike]

    # LISTS TO NUMPY ARRAYS CUZ NUMBA HATES LISTS
    strikes = np.array(strikes)
    closing_days_array = np.array(closing_days_array)
    min_profit = np.array(min_profit)

    try:
        pop, pop_error, avg_dtc, avg_dtc_error = monteCarlo(underlying, rate, sigma, days_to_expiration,
                                                              closing_days_array, trials,
                                                              initial_credit, min_profit, strikes, bsm_debit)
    except RuntimeError as err:
        print(err.args)

    response = {
        "pop": pop,
        "pop_error": pop_error,
        "avg_dtc": avg_dtc,
        "avg_dtc_error": avg_dtc_error
    }

    return response
