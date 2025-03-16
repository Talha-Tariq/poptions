import poptions

# Confused on what these variables mean? Read the README file!

# Entering existing trades: See the READMe file.

################################################################

underlying = 137.31     # Current underlying price
short_strike = 145      # Short strike price
short_price = 1.13      # Short call price
long_strike = 150
long_price = 0.4
rate = 0        # Annualized risk-free rate as a percentage (e.g. 1 year US Treasury Bill rate)
sigma = 26.8        # Implied Volatility as a percentage
days_to_expiration = 45     # Calendar days left till expiration
percentage_array = [20, 30, 40]  # Percentage of maximum profit that will trigger the position to close
closing_days_array = [21, 22, 23]       # Max calendar days passed until position is closed
trials = 2000       # Number of independent trials

print("Call Credit Spread: ", poptions.callCreditSpread(underlying, sigma, rate, trials, days_to_expiration,
                                                        closing_days_array, percentage_array, short_strike,
                                                        short_price, long_strike, long_price))

###############################################################

# underlying = 36.73
# short_strike = 28
# short_price = 0.88
# long_strike = 18
# long_price = 0.18
# rate = 0
# sigma = 71.4
# days_to_expiration = 51
# percentage_array = [75, 50]
# closing_days_array = [21, 24]
# trials = 2000
#
# print("Put Credit Spread: ", poptions.putCreditSpread(underlying, sigma, rate, trials, days_to_expiration,
#                                              closing_days_array, percentage_array, short_strike,
#                                              short_price, long_strike, long_price))
#
# ###############################################################
#
# underlying = 123
# short_strike = 120
# short_price = 6.9
# long_strike = 110
# long_price = 14.2
# rate = 0
# sigma = 29.2
# days_to_expiration = 48
# percentage_array = [20]
# closing_days_array = [48]
# trials = 2000
# #
# print("Call Debit Spread: ", poptions.callDebitSpread(underlying, sigma, rate, trials, days_to_expiration,
#                                              closing_days_array, percentage_array, short_strike,
#                                              short_price, long_strike, long_price))
#
# ###############################################################
#
# underlying = 24.87
# short_strike = 26
# short_price = 3.55
# long_strike = 28
# long_price = 4.9
# rate = 0
# sigma = 79.7
# days_to_expiration = 48
# percentage_array = [50]
# closing_days_array = [48]
# trials = 2000
#
# print("Put Debit Spread: ", poptions.putDebitSpread(underlying, sigma, rate, trials, days_to_expiration,
#                                            closing_days_array, percentage_array, short_strike,
#                                            short_price, long_strike, long_price))
#
# ###############################################################
#
# underlying = 15
# short_strike = 12.5
# short_price = 1.4
# rate = 0
# sigma = 117
# days_to_expiration = 45
# percentage_array = [50]
# closing_days_array = [21]
# trials = 2000
#
# print("Short Put: ", poptions.shortPut(underlying, sigma, rate, trials, days_to_expiration,
#                               closing_days_array, percentage_array, short_strike, short_price))
#
# ###############################################################
#
# underlying = 71.72
# short_strike = 90
# short_price = 1.16
# rate = 0
# sigma = 55
# days_to_expiration = 53
# percentage_array = [50]
# closing_days_array = [36]
# trials = 2000
#
# print("Short Call: ", poptions.shortCall(underlying, sigma, rate, trials, days_to_expiration,
#                                 closing_days_array, percentage_array, short_strike, short_price))
#
# ###############################################################
#
# underlying = 31
# long_strike = 28
# long_price = 1
# rate = 0
# sigma = 79.7
# days_to_expiration = 20
# multiple_array = [1]        # Multiple of debit paid that will trigger the position to close
# closing_days_array = [20]
# trials = 2000
#
# print("Long Put: ", poptions.longPut(underlying, sigma, rate, trials, days_to_expiration,
#                             closing_days_array, multiple_array, long_strike, long_price))
#
# ###############################################################
#
# underlying = 28
# long_strike = 31
# long_price = 1
# rate = 0
# sigma = 79.7
# days_to_expiration = 20
# multiple_array = [1]        # Multiple of debit paid that will trigger the position to close
# closing_days_array = [20]
# trials = 2000
#
# print("Long Call: ", poptions.longCall(underlying, sigma, rate, trials, days_to_expiration,
#                               closing_days_array, multiple_array, long_strike, long_price))
#
# ###############################################################
#
# underlying = 71.72
# short_strike = 90
# short_price = 1.16
# rate = 0
# sigma = 55
# days_to_expiration = 53
# percentage_array = [50]
# closing_days_array = [36]
# trials = 2000
#
# print("Covered Call: ", poptions.coveredCall(underlying, sigma, rate, trials, days_to_expiration,
#                                     closing_days_array, percentage_array, short_strike, short_price))
#
# ###############################################################
#
# underlying = 205
# rate = 0
# sigma = 68.6
# days_to_expiration = 25
# percentage_array = [50]
# closing_days_array = [25]
# trials = 2000
#
# ## PUT SIDE ###
# put_short_strike = 170
# put_short_price = 3.25
# put_long_strike = 165
# put_long_price = 2.48
#
# ## CALL SIDE ###
# call_short_strike = 250
# call_short_price = 2.82
# call_long_strike = 255
# call_long_price = 2.34
#
# print("Iron Condor: ", poptions.ironCondor(underlying, sigma, rate, trials, days_to_expiration,
#                  closing_days_array, percentage_array, put_short_strike,
#                  put_short_price, put_long_strike, put_long_price, call_short_strike,
#                  call_short_price, call_long_strike, call_long_price))
#
# ###############################################################
#
# underlying = 68.33
# call_short_strike = 82.5
# call_short_price = 0.66
# put_short_strike = 55
# put_short_price = 0.43
# rate = 0
# sigma = 51.3
# days_to_expiration = 45
# percentage_array = [50]
# closing_days_array = [24]
# trials = 2000
#
# print("Short Strangle: ", poptions.shortStrangle(underlying, sigma, rate, trials, days_to_expiration,
#                     closing_days_array, percentage_array, call_short_strike,
#                     call_short_price, put_short_strike, put_short_price))
# ###############################################################

# underlying = 198
# call_long_strike = 210
# call_long_price = 5.85
# put_long_strike = 190
# put_long_price = 7.08
# rate = 0
# sigma = 37
# days_to_expiration = 47
# multiple_array = [1]
# closing_days_array = [24]
# trials = 2000

# print("Long Strangle: ", poptions.longStrangle(underlying, sigma, rate, trials, days_to_expiration,
#                     closing_days_array, multiple_array, call_long_strike,
#                     call_long_price, put_long_strike, put_long_price))