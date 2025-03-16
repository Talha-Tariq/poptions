# poptions

Custom Python code for calculating the Probability of Profit (POP) for options trading strategies using 
Monte Carlo Simulations. The Monte Carlo Simulation runs thousands of individual stock price simulations and 
uses the data from these simulations to average out a POP number.

Unlike other calculators,
poptions lets you specify a target profit, such as a percentage of maximum profit or a multiple
of the debit paid, that will trigger your
position to close when it's reached in the simulation. Additionally, you will specify the 'closing days', which refers to the number of calendar 
days that will pass until you close the position (assuming the target profit wasn't reached to trigger the 
closing). 

**In simpler words:** the estimated POP from poptions refers to the probability of hitting a specified target profit 
within a specified number of calendar days. 

Poptions lets you add MULTIPLE combinations of target profits and closing days!

Poptions also outputs an Average Days To Close (ADTC) number. This is the estimated average number of calendar 
days you will have to wait until you reach your target profit, **assuming that the POP ended up in your favor.**

Poptions can also be used to evaluate existing trades (see below).

You can try out poptions by visiting the following website, which is powered by it: https://www.thetapopper.com/

*Disclaimer: poptions has not been vetted by any certified professional or expert. 
The calculations do not constitute investment advice. They are for educational purposes only. 
Calculations may contain mistakes and are made using models with inherent limitations that are highlighted below.
Use this tool at your own risk.*

## How does it work?

A great video explaining the underlying logic is shown here: https://www.tastytrade.com/shows/the-skinny-on-options-modeling/episodes/probability-of-50-profit-12-17-2015

In short, thousands of stock price simulations are executed in which the price change per day is modeled according to 
Geometric Brownian Motion. The Black-Scholes Model is then used to estimate the price of an options contract 
(or multiple contracts depending on the strategy used) per day in each simulation. The number of simulations in which 
the selected profit criteria is met (e.g. 50% of maximum profit within 20 calendar days) is divided by the total number of simulations, giving you 
an estimate of the POP. A similar averaging is done to acquire the ADTC. 

poptions makes the following assumptions for its simulations:
 - The stock price volatility is equal to the implied volatility and remains constant.
 - Geometric Brownian Motion is used to model the stock price.
 - Risk-free interest rates remain constant.
 - The Black-Scholes Model is used to price options contracts.
 - Dividend yield is not considered.
 - Commissions are not considered.
 - Assignment risks are not considered.
 - Earnings date and stock splits are not considered.

Of course, not all of these assumptions are true in real life and so there are limitations to this approach. For example, 
it's highly unlikely that the stock price volatility remains constant for several days. Thus, one should take these results with a grain of salt.

## How to use poptions

The **requirements.txt** file lists all the python packages (and their versions) that need to be installed for poptions to work.

A working example of a Call Credit Spread strategy is located in the **poptions_examples.py** file, as shown:
```
underlying = 137.31     # Current underlying price
short_strike = 145      # Short strike price
short_price = 1.13      # Short call price
long_strike = 150
long_price = 0.4
rate = 0        # Annualized risk-free rate as a percentage
sigma = 26.8        # Implied Volatility as a percentage
days_to_expiration = 45     # Calendar days left till expiration
percentage_array = [20, 30, 40]  # Percentage of maximum profit that will trigger the position to close
closing_days_array = [21, 22, 23]       # Max calendar days passed until position is closed
trials = 2000       # Number of independent trials

print("Call Credit Spread: ", poptions.callCreditSpread(underlying, sigma, rate, trials, days_to_expiration,
                                                        closing_days_array, percentage_array, short_strike,
                                                        short_price, long_strike, long_price))
```
The comments in the code should be self-explanatory, but the **percentage_array**, **closing_days_array**, and **trials** 
variables require some extra clarification: 
- The first elements in **percentage_array** and **closing_days_array** are 20 and 21, respectively.  
This means that our target profit is 20% of maximum profit (0.2 * (short_price - long_price) = $ 0.146). The Monte 
Carlo Simulation will consider each individual simulation (renamed to **trial** here) a success if this 
target profit is achieved. If this target profit is not reached within 21 calendar days, it will be considered 
a failure.
   
- You can add multiple combinations of target profits and closing days by simply adding extra elements 
to **percentage_array** and **closing_days_array**! In the above example, we tell the Simulation to also evaluate
  30% and 40% of maximum profits for 22 and 23 calendar days, respectively.
  
- Increasing the number of **trials** will improve the accuracy of your estimations at the cost of a slower simulation.

*Some Extra Notes:*

- Running poptions.callCreditSpread() will not output consistent results. There will always be some variance from its previous runs. This is
because a new simulation is started from scratch for every run. The amount of variance depends on how high **trials** is set: 
More trials -> higher accuracy (less variance).

- For the Long Call, Long Put, and Long Strangle strategies, **percentage_array** is replaced with **multiple_array**. This means
that the target profit is now defined as a multiple of the debit that you paid to open the position. For example, 
  if you bought a call option for $1.00, a value of [2] in **multiple_array** means that your target profit is 
  2 * $ 1.00 = $ 2.00.
  
- You can evaluate existing trades with poptions! Type the net credit received into ONE of the short price variables, 
  and leave the rest of the price variables at 0. Fill out all other variables with present data.
Example: Net credit received was $0.73 for a Call Credit Spread, so **short_price** is 0.73 and **long_price** is 0. All other
variables are filled with present data. For strategies where a net debit is paid like Debit Spreads, the debit paid
  should be in ONE of the *long* price variables, and leave the rest of the price variables at 0.

*Entering existing trades is NOT supported for **Covered Calls** unless the current underlying price is the same as it was
when you opened the position! This is because the **underlying** variable refers to the purchase price of the stock
when you opened the position.*

Running **poptions_examples.py** gives you the following output:
```
Call Credit Spread:  {'pop': [61.3, 57.65, 52.55], 'pop_error': [2.81, 2.85, 2.88], 'avg_dtc': [8.87, 10.3, 11.41], 'avg_dtc_error': [0.39, 0.43, 0.45]}
``` 
- **pop** is the probability of reaching the target profit within the closing days. The first element in **pop** 
  corresponds to the first elements in **percentage_array** and **closing_days_array**.
  
- **pop_error** is the error range for **pop**. In the above example, for the first element, 
  there is a 99% chance that the 'true' value for **pop** is between 58.49 (61.3 - 2.81) and 64.11 (61.3 + 2.81).
  Of course, this error range gets smaller as **trials** is increased.
  
- **avg_dtc** refers to the Average Days To Close (ADTC). 

- **avg_dtc_error** is the error range for **avg_dtc**.

If **avg_dtc** falls on a weekend/holiday when the markets are closed, then you can assume that the closing date 
is on the following business/trading day.

## SPEED BOOST with Numba!
If you're looking to potentially speed up simulations by 100x, the Numba python package can help you out! 
Numba translates Python functions to optimized machine code at runtime using the industry-standard LLVM compiler library.
Numba-compiled numerical algorithms in Python can approach the speeds of C or FORTRAN.

Using Numba is shockingly easy. It requires making very little modifications to our code. Follow these steps 
to speed up poptions.callCreditSpread() in **poptions_examples.py** with Numba:

Open the **CallCreditSpread.py** file. Add the following decorator to this function:
```
@jit(nopython=True, cache=True)
def bsm_debit(sim_price, strikes, rate, time_fraction, sigma):
    ...

``` 
Open the **MonteCarlo.py** file. Add the decorator to this function:
```
@jit(nopython=True, cache=True)
def monteCarlo(underlying, rate, sigma, days_to_expiration, closing_days_array, trials, initial_credit,
                   min_profit, strikes, bsm_func):
    ...
``` 
Open the **BlackScholes.py** file. Add the decorator to the functions:
```
@jit(nopython=True, cache=True)
def blackScholesPut(s, k, rr, tt, sd):
    ...
    
@jit(nopython=True, cache=True)
def blackScholesCall(s, k, rr, tt, sd):
    ...
``` 

You're good to go, but you MUST account for the following: The first time you call poptions.callCreditSpread() will be slow 
(around a few seconds) since it triggers a compilation step for Numba. The second poptions.callCreditSpread() call is 
where you'll see the performance gains. Here's a comparison of the speeds between calls:
```
First poptions.callCreditSpread() call WITH Numba Compilation: 1.756 seconds
Second poptions.callCreditSpread() call WITHOUT Numba Compilation: 0.0064 seconds
```

## Donations
If you like the project and feel like donating some crypto to the author(s), you can do so here:

BTC: 16xbCyVZB3x3PNFs1qQEXGsNgtTd4BKE6z

LTC: Lg1d1VEd5DMQzycZTSSeDEc59yomwDwX8j

Thank you!

## License
MIT License

A description of this license can be found in the **LICENSE.txt** file.
