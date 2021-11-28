import numpy as np
from numba import jit, prange

# Assumptions:
# Volatility remains constant throughout the option's life
# Dividend yield is not considered in the option's pricing model
# The stock price is log-normally distributed
# *** It would be better to use historical volatility here since IV tends to overstate
# realized volatility. More specifically, use the historical per annum 1 standard deviation
# percentage move of the stock instead.


# @jit(nopython=True, cache=True, parallel=True)
@jit(nopython=True, cache=True)
def poptions_numba(underlying, rate, sigma, DTE, closing_DTE, trials, initial_credit, min_profit, strikes, bsm_func):

    dt = 1 / 365  # 365 calendar days in a year
    # dt = 1 / 252  # 252 trading days in a year

    length = len(closing_DTE)

    # Days
    closing_DTE_max = max(closing_DTE)
    days_to_close = closing_DTE_max

    # Simulating stock price
    sigma = sigma / 100
    rate = rate / 100

    counter1 = [0] * length
    profit_dte = [0] * length
    # profit_dte_history = np.zeros([length, trials]) # Numba doesn't like it this way (StackOverflow)
    profit_dte_history = np.zeros((length, trials))

    epsilon_cum = 0
    t_cum = 0
    indices = [0] * length

    # Calculating option prices
    for c in range(trials):
    # for c in prange(trials):

        for i in range(length):
            indices[i] = 0

        # +1 added to account for first day. sim_prices[0,...] = underlying price.
        for r in range(days_to_close + 1):
        # for r in prange(days_to_close + 1):

            # Brownian Motion
            W = (dt ** (1 / 2)) * epsilon_cum

            # Geometric Brownian Motion
            signal = (rate - 0.5 * (sigma ** 2)) * t_cum
            noise = sigma * W
            y = noise + signal
            sim_prices = underlying * np.exp(y)

            epsilon = np.random.randn()
            # epsilon_cum = epsilon_cum + epsilon
            epsilon_cum += epsilon

            # t_cum = t_cum + dt
            t_cum += dt

            if sim_prices <= 0:
                sim_prices = 0.001

            debit = bsm_func(sim_prices, strikes, rate, dt * (DTE - r), sigma)

            profit = initial_credit - debit

            sum = 0

            for i in range(length):
            # for i in prange(length):
                if indices[i] == 1:
                    sum += 1
                    continue
                else:
                    if min_profit[i] <= profit:
                        counter1[i] += 1
                        profit_dte[i] += r
                        profit_dte_history[i, c] = r

                        indices[i] = 1
                        sum += 1
                    elif r >= closing_DTE[i]:
                        indices[i] = 1
                        sum += 1

            if sum == length:
                break

        epsilon_cum = 0
        t_cum = 0

    pop_counter1 = [c / trials * 100 for c in counter1]
    pop_counter1 = [round(x, 2) for x in pop_counter1]

    # print("pop_counter1: ", pop_counter1)

    pop_counter1_err = [2.58 * (x * (100 - x) / trials) ** (1 / 2) for x in pop_counter1]
    pop_counter1_err = [round(x, 2) for x in pop_counter1_err]

    # print("pop_counter1_err: ", pop_counter1_err)

    avg_dte = []
    avg_dte_err = []

    for index in range(length):
        if counter1[index] > 0:
            avg_dte.append(profit_dte[index] / counter1[index])

            n_a = counter1[index]
            mu_hat_a = profit_dte[index] / n_a
            summation = 0

            for value in profit_dte_history[index, :]:
                if value == 0:  # if 0 then it means that min_profit wasn't hit
                    continue

                summation = summation + (value - mu_hat_a) ** 2

            s_a_squared = (1 / n_a) * summation  # changed from n_a - 1 for simplicity
            std_dev = ((n_a - 1) * s_a_squared) ** (1 / 2) / n_a
            avg_dte_err.append(2.58 * std_dev)

        else:
            avg_dte.append(0)
            avg_dte_err.append(0)

    avg_dte = [round(x, 2) for x in avg_dte]

    # print("avg_dte: ", avg_dte)

    avg_dte_err = [round(x, 2) for x in avg_dte_err]

    # print("avg_dte_err: ", avg_dte_err)

    return pop_counter1, pop_counter1_err, avg_dte, avg_dte_err
