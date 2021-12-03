from numba import jit
from MonteCarlo import monteCarlo
import time
from BlackScholes import blackScholesCall
import numpy as np


def bsm_debit(sim_price, strikes, rate, time_fraction, sigma):
    P_short_calls = blackScholesCall(sim_price, strikes[0], rate, time_fraction, sigma)

    debit = P_short_calls
    credit = sim_price
    debit = debit - credit

    return debit


def coveredCall(underlying, sigma, rate, trials, days_to_expiration,
                closing_days_array, percentage_array, short_strike, short_price):

    for closing_days in closing_days_array:
        if closing_days > days_to_expiration:
            raise ValueError("Closing days cannot be beyond Days To Expiration.")

    if len(closing_days_array) != len(percentage_array):
        raise ValueError("closing_days_array and percentage_array sizes must be equal.")

    # SIMULATION
    initial_credit = short_price  # Credit received from opening trade
    stock_debit = underlying  # Assuming current underlying price = purchase price
    initial_credit = initial_credit - stock_debit

    percentage_array = [x / 100 for x in percentage_array]
    max_profit = short_price + (short_strike - underlying)
    min_profit = [max_profit * x for x in percentage_array]

    strikes = [short_strike]

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