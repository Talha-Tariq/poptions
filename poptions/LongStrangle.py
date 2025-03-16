from numba import jit
from MonteCarlo import monteCarlo
import time
from BlackScholes import blackScholesCall, blackScholesPut
import numpy as np


def bsm_debit(sim_price, strikes, rate, time_fraction, sigma):
    P_long_calls = blackScholesCall(sim_price, strikes[0], rate, time_fraction, sigma)
    P_long_puts = blackScholesPut(sim_price, strikes[1], rate, time_fraction, sigma)

    credit = P_long_calls + P_long_puts
    debit = -credit

    return debit


def longStrangle(underlying, sigma, rate, trials, days_to_expiration,
                  closing_days_array, multiple_array, call_long_strike,
                  call_long_price, put_long_strike, put_long_price):

    # Data Verification
    if call_long_strike < put_long_strike:
        raise ValueError("Call Strike cannot be less than Put Strike")

    for closing_days in closing_days_array:
        if closing_days > days_to_expiration:
            raise ValueError("Closing days cannot be beyond Days To Expiration.")

    if len(closing_days_array) != len(multiple_array):
        raise ValueError("closing_days_array and multiple_array sizes must be equal.")

    # SIMULATION
    initial_debit = call_long_price + put_long_price  # Debit paid from opening trade
    initial_credit = -1 * initial_debit

    min_profit = [initial_debit * x for x in multiple_array]

    strikes = [call_long_strike, put_long_strike]

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
