from CallCreditSpread_modified import callCreditSpread
from PutCreditSpread_modified import putCreditSpread
from CallDebitSpread_modified import callDebitSpread
from PutDebitSpread_modified import putDebitSpread
from ShortPut_modified import shortPut
from ShortCall_modified import shortCall
from LongPut_modified import longPut
from LongCall_modified import longCall
from CoveredCall_modified import coveredCall
from IronCondor_modified import ironCondor
from ShortStrangle_modified import shortStrangle


# TO DO:
# don't need contracts
# Change variable names like DTE since they dont make sense now
# data validation step
# rearrange function variable order so that master vars are first for convenience
# verify outputs with thetapopper
# Note that entering existing trades not possible for CC
# More comments?

################################################################

underlying = 137.31     # current underlying price
short_strike = 145
short_price = 1.13     # short call price(credit)
long_strike = 150
long_price = 0      # long call price(debit)
rate = 0               # risk free annual rate as a decimal
sigma = 26.8      # IV as a fraction (see note in: ***)
DTE = 45               # Days To Expiration
fraction = [20, 30, 40, 50]
# fraction = [45]
closing_DTE = [21, 21, 21, 21]  # DTE when the trade is closed
# closing_DTE = [21]
nTrials = 2000         # Number of independent trials / simulations
contracts = 1

print("Call Credit Spread: ", callCreditSpread(nTrials, short_strike, short_price, long_strike, long_price,
                     underlying, rate, sigma, DTE, fraction, closing_DTE, contracts))

################################################################

# underlying = 36.73  # current underlying price
# short_strike = 28
# short_price = 0.88  # short put price(credit)
# long_strike = 18
# long_price = 0.18  # long put price(debit)
# rate = 0  # risk free annual rate as a decimal
# sigma = 71.4   # IV as a fraction (see note in: ***)
# DTE = 51  # Days To Expiration
# fraction = [75, 50]  # Desired minimum percentage of max profit as a fraction
# closing_DTE = [21, 24]  # DTE when the trade is closed
# nTrials = 2000  # Number of independent trials / simulations
# contracts = 1
#
# print("Put Credit Spread: ", putCreditSpread(nTrials, short_strike, short_price, long_strike, long_price,
#                      underlying, rate, sigma, DTE, fraction, closing_DTE, contracts))

################################################################

# underlying = 123     # current underlying price
# short_strike = 120
# short_price = 6.9     # short call price(credit)
# long_strike = 110
# long_price = 14.2      # long call price(debit)
# rate = 0               # risk free annual rate as a decimal
# sigma = 29.2     # IV as a fraction (see note in: ***)
# DTE = 48               # Days To Expiration
# fraction = [20]   # Desired minimum percentage of max profit as a fraction
# closing_DTE = [48]       # DTE when the trade is closed
# nTrials = 2000         # Number of independent trials / simulations
# contracts = 1
#
# print("Call Debit Spread: ", callDebitSpread(nTrials, short_strike, short_price, long_strike, long_price,
#                      underlying, rate, sigma, DTE, fraction, closing_DTE, contracts))

################################################################

# underlying = 24.87     # current underlying price
# short_strike = 26
# short_price = 3.55     # short put price(credit)
# long_strike = 28
# long_price = 4.9      # long put price(debit)
# rate = 0               # risk free annual rate as a decimal
# sigma = 79.7     # IV as a fraction (see note in: ***)
# DTE = 48               # Days To Expiration
# fraction = [50]     # Desired minimum percentage of max profit as a fraction
# closing_DTE = [48]       # DTE when the trade is closed
# nTrials = 2000         # Number of independent trials / simulations
# contracts = 1
#
# print("Put Debit Spread: ", putDebitSpread(nTrials, short_strike, short_price, long_strike, long_price,
#                      underlying, rate, sigma, DTE, fraction, closing_DTE, contracts))

################################################################

# underlying = 15         # current underlying price
# short_strike = 12.5           # strike price
# short_price = 1.4         # current call option price
# rate = 0                # risk free annual rate as a decimal
# sigma = 117        # IV as a fraction (see note in: ***)
# DTE = 45                # Days To Expiration
# fraction = [50]     # Desired minimum percentage of max profit as a fraction
# closing_DTE = [21]        # DTE when the trade is closed
# nTrials = 2000          # Number of independent trials/simulations
# contracts = 1
#
# print("Short Put: ", shortPut(nTrials, short_strike, short_price,
#                      underlying, rate, sigma, DTE, fraction, closing_DTE, contracts))

################################################################

# underlying = 71.72         # current underlying price
# short_strike = 90           # strike price
# short_price = 1.16         # current call option price
# rate = 0                # risk free annual rate as a decimal
# sigma = 55     # IV as a fraction (see note in: ***)
# DTE = 53                # Days To Expiration
# fraction = [50]     # Desired minimum percentage of max profit as a fraction
# closing_DTE = [36]        # DTE when the trade is closed
# nTrials = 2000          # Number of independent trials/simulations
# contracts = 1
#
# print("Short Call: ", shortCall(nTrials, short_strike, short_price,
#                      underlying, rate, sigma, DTE, fraction, closing_DTE, contracts))

################################################################

# underlying = 31
# long_strike = 28
# long_price = 1
# rate = 0
# sigma = 79.7
# DTE = 20
# fraction = [1]
# closing_DTE = [20]
# nTrials = 2000
# contracts = 1
#
# print("Long Put: ", longPut(nTrials, long_strike, long_price,
#                      underlying, rate, sigma, DTE, fraction, closing_DTE, contracts))

################################################################

# underlying = 28
# long_strike = 31
# long_price = 1
# rate = 0
# sigma = 79.7
# DTE = 20
# fraction = [1]
# closing_DTE = [20]
# nTrials = 2000
# contracts = 1
#
# print("Long Call: ", longCall(nTrials, long_strike, long_price,
#                      underlying, rate, sigma, DTE, fraction, closing_DTE, contracts))

################################################################

# underlying = 71.72         # current underlying price
# short_strike = 90           # strike price
# short_price = 1.16         # current call option price
# rate = 0                # risk free annual rate as a decimal
# sigma = 55     # IV as a fraction (see note in: ***)
# DTE = 53                # Days To Expiration
# fraction = [50]     # Desired minimum percentage of max profit as a fraction
# closing_DTE = [36]        # DTE when the trade is closed
# nTrials = 2000          # Number of independent trials/simulations
# contracts = 1
#
# print("Covered Call: ", coveredCall(nTrials, short_strike, short_price,
#                      underlying, rate, sigma, DTE, fraction, closing_DTE, contracts))

################################################################

# underlying = 205     # current underlying price
# rate = 0               # risk free annual rate as a decimal
# sigma = 68.6    # IV as a fraction (see note in: ***)
# DTE = 25               # Days To Expiration
# fraction = [50]   # Desired minimum percentage of max profit as a fraction
# closing_DTE = [25]       # DTE when the trade is closed
# nTrials = 2000         # Number of independent trials / simulations
#
# ## PUT SIDE ###
# put_short_strike = 170
# put_short_price = 3.25     # short put price(credit)
# put_long_strike = 165
# put_long_price = 2.48      # long put price(debit)
#
# ## CALL SIDE ###
# call_short_strike = 250
# call_short_price = 2.82     # short call price(credit)
# call_long_strike = 255
# call_long_price = 2.34      # long call price(debit)
#
# contracts = 1
#
# print(ironCondor(nTrials, call_short_strike, call_short_price, call_long_strike, call_long_price,
#                     put_short_strike, put_short_price, put_long_strike, put_long_price,
#                     underlying, rate, sigma, DTE, fraction, closing_DTE,
#                     contracts))

################################################################

# underlying = 68.33
# call_strike = 82.5
# call_price = 0.66
# put_strike = 55
# put_price = 0.43
# rate = 0
# sigma = 51.3
# DTE = 45
# fraction = [50]
# # fraction = [20, 30, 40, 50]
# closing_DTE = [24]
# # closing_DTE = [21, 21, 21, 21]
# nTrials = 2000
# contracts = 1
#
# print(shortStrangle(nTrials, call_strike, call_price, put_strike, put_price,
#                      underlying, rate, sigma, DTE, fraction, closing_DTE, contracts))