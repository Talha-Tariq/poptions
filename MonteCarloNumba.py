import numpy as np
from numba import jit

# Assumptions:
# Volatility remains constant throughout the option's life
# Dividend yield is not considered in the option's pricing model
# The stock price is log-normally distributed


@jit(nopython=True, cache=True)
def monteCarloNumba(underlying, rate, sigma, days_to_expiration, closing_days_array, trials, initial_credit,
                   min_profit, strikes, bsm_func):

    dt = 1 / 365  # 365 calendar days in a year

    length = len(closing_days_array)
    max_closing_days = max(closing_days_array)

    # Simulating stock price
    sigma = sigma / 100
    rate = rate / 100

    counter1 = [0] * length
    profit_dtc = [0] * length
    # profit_dte_history = np.zeros([length, trials]) # Numba doesn't like it this way (StackOverflow)
    profit_dtc_history = np.zeros((length, trials))

    epsilon_cum = 0
    t_cum = 0
    indices = [0] * length

    # Calculating option prices
    for c in range(trials):

        for i in range(length):
            indices[i] = 0

        # +1 added to account for first day. sim_prices[0,...] = underlying price.
        for r in range(max_closing_days + 1):

            # Brownian Motion
            W = (dt ** (1 / 2)) * epsilon_cum

            # Geometric Brownian Motion
            signal = (rate - 0.5 * (sigma ** 2)) * t_cum
            noise = sigma * W
            y = noise + signal
            sim_prices = underlying * np.exp(y)

            epsilon = np.random.randn()
            epsilon_cum += epsilon

            t_cum += dt

            if sim_prices <= 0:
                sim_prices = 0.001

            debit = bsm_func(sim_prices, strikes, rate, dt * (days_to_expiration - r), sigma)

            profit = initial_credit - debit
            sum = 0

            for i in range(length):
                if indices[i] == 1:
                    sum += 1
                    continue
                else:
                    if min_profit[i] <= profit:
                        counter1[i] += 1
                        profit_dtc[i] += r
                        profit_dtc_history[i, c] = r

                        indices[i] = 1
                        sum += 1
                    elif r >= closing_days_array[i]:
                        indices[i] = 1
                        sum += 1

            if sum == length:
                break

        epsilon_cum = 0
        t_cum = 0

    pop_counter1 = [c / trials * 100 for c in counter1]
    pop_counter1 = [round(x, 2) for x in pop_counter1]

    pop_counter1_err = [2.58 * (x * (100 - x) / trials) ** (1 / 2) for x in pop_counter1]
    pop_counter1_err = [round(x, 2) for x in pop_counter1_err]

    avg_dtc = []  # Average days to close
    avg_dtc_error = []

    for index in range(length):
        if counter1[index] > 0:
            avg_dtc.append(profit_dtc[index] / counter1[index])

            n_a = counter1[index]
            mu_hat_a = profit_dtc[index] / n_a
            summation = 0

            for value in profit_dtc_history[index, :]:
                if value == 0:  # if 0 then it means that min_profit wasn't hit
                    continue

                summation = summation + (value - mu_hat_a) ** 2

            s_a_squared = (1 / n_a) * summation  # changed from n_a - 1 for simplicity
            std_dev = ((n_a - 1) * s_a_squared) ** (1 / 2) / n_a
            avg_dtc_error.append(2.58 * std_dev)

        else:
            avg_dtc.append(0)
            avg_dtc_error.append(0)

    avg_dtc = [round(x, 2) for x in avg_dtc]

    avg_dtc_error = [round(x, 2) for x in avg_dtc_error]

    return pop_counter1, pop_counter1_err, avg_dtc, avg_dtc_error
