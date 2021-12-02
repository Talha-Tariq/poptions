import time
from flask import Flask, make_response
from flask_restful import Api, Resource, reqparse, abort
from token_validation import requires_auth, requires_scope, get_token_auth_header
from jose import jwt
from flask_cors import CORS
import redis
from CallCreditSpread import callCreditSpread
from PutCreditSpread import putCreditSpread
from ShortPut import shortPut
from ShortCall import shortCall
from ShortStrangle import shortStrangle
from LongPut import longPut
from LongCall import longCall
from PutDebitSpread import putDebitSpread
from CallDebitSpread import callDebitSpread
from IronCondor import ironCondor
from CoveredCall import coveredCall
from token_validation_new import requires_auth_new
import os

############################### TO DO #######################################

# Notes:
# When using prange, can get different POP for same combo values.
# time.time in docker is off by 20 seconds. Seems to work fine in deployment though.

# TO DO:
# FRONTEND AND BACKEND:


# BACKEND:


# different rate limit if using browser? how to justify rate limiting depending on client? (NOT URGENT)
# why with prange does second combo affect pop of first combo? (NOT URGENT)
# Think about saving trades system (NOT URGENT)
# Email service? Can Azure handle this? (NOT URGENT)
	# Should be done on frontend? Makes more sense.
	# Flask SMTP if backend
# Payment system + separate graph api: (NOT URGENT)
# RATE LIMTING. PREVENT SPAMMING OF CREDIT CARD PROCESSOR. GET CHARGED FOR DECLINED CREDIT CARDS.


# FRONTEND:

############################### Setup #######################################

# Redis location: C:\Program Files\Redis

# FOR DOCKER-COMPOSE:
# rc = redis.Redis(host='redis', port=6379, db=0)

app = Flask(__name__)
CORS(app)
api = Api(app)


class Range(object):
	def __init__(self, start, end):
		self.start = start
		self.end = end

	def __eq__(self, other):
		return self.start <= other <= self.end


# Master Keys
underlying_key = 'underlying'
rate_key = 'riskfreerate'
sigma_key = 'impliedvol'
dte_key = 'dte'
fraction_key = 'percentage_array'
closing_dte_key = 'closingdte'
contracts_key = 'contracts'
# trials_key = 'trials'

# Spread + Single Short Option Keys
short_strike_key = 'shortstrike'
short_price_key = 'shortprice'
long_strike_key = 'longstrike'
long_price_key = 'longprice'

# Short Strangle Keys
call_strike_key = 'callstrike'
call_price_key = 'callprice'
put_strike_key = 'putstrike'
put_price_key = 'putprice'

# iron Condor Keys
call_short_strike_key = 'call_short_strike'
call_short_price_key = 'call_short_price'
call_long_strike_key = 'call_long_strike'
call_long_price_key = 'call_long_price'
put_short_strike_key = 'put_short_strike'
put_short_price_key = 'put_short_price'
put_long_strike_key = 'put_long_strike'
put_long_price_key = 'put_long_price'

# Master Parser
post_args = reqparse.RequestParser()
post_args.add_argument(underlying_key, type=float, required=True, choices=[Range(0.001, 20000.0)])
post_args.add_argument(rate_key, type=float, required=True, choices=[Range(0.0, 100.0)])
post_args.add_argument(sigma_key, type=float, required=True, choices=[Range(0.001, 2000.0)])
post_args.add_argument(dte_key, type=int, required=True, choices=range(1, 93+1))
post_args.add_argument(fraction_key, type=float, required=True, action='append', choices=[Range(0.001, 100.0)])
post_args.add_argument(closing_dte_key, type=int, required=True, action='append', choices=range(0, 93+1))
post_args.add_argument(contracts_key, type=int, required=True, choices=range(1, 1000+1))
# post_args.add_argument(trials_key, type=int, required=True, choices=range(1, 2000+1))

# Credit Spread Parser
cs_post_args = post_args.copy()
cs_post_args.add_argument(short_strike_key, type=float, required=True, choices=[Range(0.001, 20000.0)])
cs_post_args.add_argument(short_price_key, type=float, required=True, choices=[Range(0, 20000.0)])
cs_post_args.add_argument(long_strike_key, type=float, required=True, choices=[Range(0.001, 20000.0)])
cs_post_args.add_argument(long_price_key, type=float, required=True, choices=[Range(0, 20000.0)])

# Debit Spread Parser
ds_post_args = post_args.copy()
ds_post_args.add_argument(short_strike_key, type=float, required=True, choices=[Range(0.001, 20000.0)])
ds_post_args.add_argument(short_price_key, type=float, required=True, choices=[Range(0, 20000.0)])
ds_post_args.add_argument(long_strike_key, type=float, required=True, choices=[Range(0.001, 20000.0)])
ds_post_args.add_argument(long_price_key, type=float, required=True, choices=[Range(0, 20000.0)])

# Single Short Option Parser
so_post_args = post_args.copy()
so_post_args.add_argument(short_strike_key, type=float, required=True, choices=[Range(0.001, 20000.0)])
so_post_args.add_argument(short_price_key, type=float, required=True, choices=[Range(0.001, 20000.0)])

# Single Long Option Parser
sl_post_args = post_args.copy()
sl_post_args.add_argument(long_strike_key, type=float, required=True, choices=[Range(0.001, 20000.0)])
sl_post_args.add_argument(long_price_key, type=float, required=True, choices=[Range(0.001, 20000.0)])

# Short Strangle Parser
ss_post_args = post_args.copy()
ss_post_args.add_argument(call_strike_key, type=float, required=True, choices=[Range(0.001, 20000.0)])
ss_post_args.add_argument(call_price_key, type=float, required=True, choices=[Range(0, 20000.0)])
ss_post_args.add_argument(put_strike_key, type=float, required=True, choices=[Range(0.001, 20000.0)])
ss_post_args.add_argument(put_price_key, type=float, required=True, choices=[Range(0, 20000.0)])

# Short Iron Condor Parser
ic_post_args = post_args.copy()
ic_post_args.add_argument(call_short_strike_key, type=float, required=True, choices=[Range(0.001, 20000.0)])
ic_post_args.add_argument(call_short_price_key, type=float, required=True, choices=[Range(0, 20000.0)])
ic_post_args.add_argument(call_long_strike_key, type=float, required=True, choices=[Range(0.001, 20000.0)])
ic_post_args.add_argument(call_long_price_key, type=float, required=True, choices=[Range(0, 20000.0)])
ic_post_args.add_argument(put_short_strike_key, type=float, required=True, choices=[Range(0.001, 20000.0)])
ic_post_args.add_argument(put_short_price_key, type=float, required=True, choices=[Range(0, 20000.0)])
ic_post_args.add_argument(put_long_strike_key, type=float, required=True, choices=[Range(0.001, 20000.0)])
ic_post_args.add_argument(put_long_price_key, type=float, required=True, choices=[Range(0, 20000.0)])


def arr_limiting(args, dte_key, fraction_key, closing_dte_key, free_limit, gold_limit, token):
	DTE = args[dte_key]
	fraction = args[fraction_key]
	closing_DTE = args[closing_dte_key]

	# Data Verification
	for closing_dte in closing_DTE:
		if closing_dte > DTE:
			return abort(400, message={closing_dte_key: "Closing date cannot be beyond Expiration date."})

	if len(closing_DTE) != len(fraction):
		return abort(400, message={closing_dte_key: "Closing days_to_expiration and Fraction array lengths must be equal."})

	try:
		unverified_claims = jwt.get_unverified_claims(token)  # don't really need try catch if wrapper verifies token
	except Exception:
		return abort(401, message="Bearer token is invalid.")

	memb_claim = unverified_claims.get("extension_Membership")

	if memb_claim == "free":
		if len(closing_DTE) > free_limit:
			return abort(400, message="Exceeded the number of combinations limit of " + str(free_limit))
	elif memb_claim == "gold":
		if len(closing_DTE) > gold_limit:
			return abort(400, message="Exceeded the number of combinations limit of " + str(gold_limit))
	else:
		return abort(401, message="No membership found. Please contact the administrator to report this issue.")


############################### Endpoints #######################################

arr_free_limit = int(os.environ["FLASK_ARR_FREE_LIMIT"])
arr_gold_limit = int(os.environ["FLASK_ARR_GOLD_LIMIT"])
nTrials = int(os.environ["FLASK_TRIALS"]) 

class CallCreditSpread(Resource):
	# @requires_auth_new
	def post(self):

		# if not requires_scope("access_as_user"):
		# 	return abort(403, message="You don't have authorization to access this resource.")

		# Successfully authenticated and authorized

		# token = get_token_auth_header()  # <------- AFTER VALIDATION

		args = cs_post_args.parse_args()

		# arr_limiting(args, dte_key, fraction_key, closing_dte_key, arr_free_limit, arr_gold_limit, token)

		response = callCreditSpread(args, nTrials, short_strike_key, short_price_key, long_strike_key, long_price_key,
		underlying_key, rate_key, sigma_key, dte_key, fraction_key, closing_dte_key, contracts_key)

		return response


class PutCreditSpread(Resource):
	# @requires_auth_new
	def post(self):

		# if not requires_scope("access_as_user"):
		# 	return abort(403, message="You don't have authorization to access this resource.")

		# Successfully authenticated and authorized

		# token = get_token_auth_header()  # <------- AFTER VALIDATION

		args = cs_post_args.parse_args()

		# arr_limiting(args, dte_key, fraction_key, closing_dte_key, arr_free_limit, arr_gold_limit, token)

		response = putCreditSpread(args, nTrials, short_strike_key, short_price_key, long_strike_key, long_price_key,
									underlying_key, rate_key, sigma_key, dte_key, fraction_key, closing_dte_key,
									contracts_key)

		return response


class ShortPut(Resource):
	# @requires_auth_new
	def post(self):

		# start = time.perf_counter()

		# if not requires_scope("access_as_user"):
		# 	return abort(403, message="You don't have authorization to access this resource.")

		# Successfully authenticated and authorized

		# token = get_token_auth_header()  # <------- AFTER VALIDATION

		args = so_post_args.parse_args()

		# arr_limiting(args, dte_key, fraction_key, closing_dte_key, arr_free_limit, arr_gold_limit, token)

		response = shortPut(args, nTrials, short_strike_key, short_price_key,
									underlying_key, rate_key, sigma_key, dte_key, fraction_key, closing_dte_key,
									contracts_key)

		# end = time.perf_counter()
		# print("SHORT PUT EXECUTION TIME:")
		# print(end - start)

		return response


class ShortCall(Resource):
	# @requires_auth_new
	def post(self):

		# if not requires_scope("access_as_user"):
		# 	return abort(403, message="You don't have authorization to access this resource.")

		# Successfully authenticated and authorized

		# token = get_token_auth_header()  # <------- AFTER VALIDATION

		args = so_post_args.parse_args()

		# arr_limiting(args, dte_key, fraction_key, closing_dte_key, arr_free_limit, arr_gold_limit, token)

		response = shortCall(args, nTrials, short_strike_key, short_price_key,
									underlying_key, rate_key, sigma_key, dte_key, fraction_key, closing_dte_key,
									contracts_key)

		return response


class ShortStrangle(Resource):
	# @requires_auth_new
	def post(self):

		# if not requires_scope("access_as_user"):
		# 	return abort(403, message="You don't have authorization to access this resource.")

		# Successfully authenticated and authorized

		# token = get_token_auth_header()  # <------- AFTER VALIDATION

		args = ss_post_args.parse_args()

		# arr_limiting(args, dte_key, fraction_key, closing_dte_key, arr_free_limit, arr_gold_limit, token)

		response = shortStrangle(args, nTrials, call_strike_key, call_price_key, put_strike_key, put_price_key,
									underlying_key, rate_key, sigma_key, dte_key, fraction_key, closing_dte_key,
									contracts_key)

		return response


class LongPut(Resource):
	# @requires_auth_new
	def post(self):

		# if not requires_scope("access_as_user"):
		# 	return abort(403, message="You don't have authorization to access this resource.")

		# Successfully authenticated and authorized

		# token = get_token_auth_header()  # <------- AFTER VALIDATION

		args = sl_post_args.parse_args()

		# arr_limiting(args, dte_key, fraction_key, closing_dte_key, arr_free_limit, arr_gold_limit, token)

		response = longPut(args, nTrials, long_strike_key, long_price_key,
									underlying_key, rate_key, sigma_key, dte_key, fraction_key, closing_dte_key,
									contracts_key)

		return response


class LongCall(Resource):
	# @requires_auth_new
	def post(self):

		# if not requires_scope("access_as_user"):
		# 	return abort(403, message="You don't have authorization to access this resource.")

		# Successfully authenticated and authorized

		# token = get_token_auth_header()  # <------- AFTER VALIDATION

		args = sl_post_args.parse_args()

		# arr_limiting(args, dte_key, fraction_key, closing_dte_key, arr_free_limit, arr_gold_limit, token)

		response = longCall(args, nTrials, long_strike_key, long_price_key,
									underlying_key, rate_key, sigma_key, dte_key, fraction_key, closing_dte_key,
									contracts_key)

		return response


class PutDebitSpread(Resource):
	# @requires_auth_new
	def post(self):

		# if not requires_scope("access_as_user"):
		# 	return abort(403, message="You don't have authorization to access this resource.")

		# Successfully authenticated and authorized

		# token = get_token_auth_header()  # <------- AFTER VALIDATION

		args = ds_post_args.parse_args()

		# arr_limiting(args, dte_key, fraction_key, closing_dte_key, arr_free_limit, arr_gold_limit, token)

		response = putDebitSpread(args, nTrials, short_strike_key, short_price_key, long_strike_key, long_price_key,
									underlying_key, rate_key, sigma_key, dte_key, fraction_key, closing_dte_key,
									contracts_key)

		return response


class CallDebitSpread(Resource):
	# @requires_auth_new
	def post(self):

		# if not requires_scope("access_as_user"):
		# 	return abort(403, message="You don't have authorization to access this resource.")

		# Successfully authenticated and authorized

		# token = get_token_auth_header()  # <------- AFTER VALIDATION

		args = ds_post_args.parse_args()

		# arr_limiting(args, dte_key, fraction_key, closing_dte_key, arr_free_limit, arr_gold_limit, token)

		response = callDebitSpread(args, nTrials, short_strike_key, short_price_key, long_strike_key, long_price_key,
									underlying_key, rate_key, sigma_key, dte_key, fraction_key, closing_dte_key,
									contracts_key)

		return response


class IronCondor(Resource):
	# @requires_auth_new
	def post(self):

		# if not requires_scope("access_as_user"):
		# 	return abort(403, message="You don't have authorization to access this resource.")

		# Successfully authenticated and authorized

		# token = get_token_auth_header()  # <------- AFTER VALIDATION

		args = ic_post_args.parse_args()

		# arr_limiting(args, dte_key, fraction_key, closing_dte_key, arr_free_limit, arr_gold_limit, token)

		response = ironCondor(args, nTrials, call_short_strike_key, call_short_price_key, call_long_strike_key,
							  call_long_price_key,
							  put_short_strike_key, put_short_price_key, put_long_strike_key, put_long_price_key,
							  underlying_key, rate_key, sigma_key, dte_key, fraction_key, closing_dte_key,
							  contracts_key)

		return response


class CoveredCall(Resource):
	# @requires_auth_new
	def post(self):

		# if not requires_scope("access_as_user"):
		# 	return abort(403, message="You don't have authorization to access this resource.")

		# Successfully authenticated and authorized

		# token = get_token_auth_header()  # <------- AFTER VALIDATION

		args = so_post_args.parse_args()

		# arr_limiting(args, dte_key, fraction_key, closing_dte_key, arr_free_limit, arr_gold_limit, token)

		response = coveredCall(args, nTrials, short_strike_key, short_price_key,
							 underlying_key, rate_key, sigma_key, dte_key, fraction_key, closing_dte_key,
							 contracts_key)

		# # TESTINGGGG
		# response_body = {
		# 	"pop": [69],
		# 	"pop_error": [2],
		# 	"avg_days": [42],
		# 	"avg_days_err": [1]
		# }
		# response = make_response(response_body, 200)

		return response


# class Time(Resource):
# 	@requires_auth
# 	def get(self):
# 		return {'time': time.time()}  # automatically jsonified as dictionary
# 		# return jsonify({'time': time.time()})


# api.add_resource(Hello, "/api/hello")
# api.add_resource(Time, "/api/time")
api.add_resource(CallCreditSpread, "/api/simulate/callcreditspread")
api.add_resource(PutCreditSpread, "/api/simulate/putcreditspread")
api.add_resource(ShortPut, "/api/simulate/shortput")
api.add_resource(ShortCall, "/api/simulate/shortcall")
api.add_resource(ShortStrangle, "/api/simulate/shortstrangle")
api.add_resource(LongPut, "/api/simulate/longput")
api.add_resource(LongCall, "/api/simulate/longcall")
api.add_resource(PutDebitSpread, "/api/simulate/putdebitspread")
api.add_resource(CallDebitSpread, "/api/simulate/calldebitspread")
api.add_resource(IronCondor, "/api/simulate/ironcondor")
api.add_resource(CoveredCall, "/api/simulate/coveredcall")

# if __name__ == '__main__':
# 	app.run(debug=True)

# def simplyparsing(args, underlying_key, rate_key, sigma_key, dte_key, fraction_key, closing_dte_key, contracts_key):
#
# 	underlying = args[underlying_key]
# 	rate = args[rate_key]
# 	sigma = args[sigma_key]
# 	days_to_expiration = args[dte_key]
# 	percentage_array = args[fraction_key]
# 	closing_days_array = args[closing_dte_key]
# 	contracts = args[contracts_key]
#
# 	return underlying, rate, sigma, days_to_expiration, percentage_array, closing_days_array, contracts

# class Hello(Resource):
# 	@requires_auth
# 	def get(self):
#
# 		if not requires_scope("access_as_user"):
# 			abort(403, message="You don't have authorization to access to this resource")
#
# 		### Successfuly authenticated and authorized ###
#
# 		token = get_token_auth_header()  # <------- AFTER VALIDATION
# 		free_limit = 5
# 		gold_limit = 15
#
# 		rate_limiting(free_limit, gold_limit, token)

# def timer_minutes(start, end):
# 	hours, rem = divmod(end - start, 3600)
# 	minutes, seconds = divmod(rem, 60)
# 	return int(minutes)  # FLOAT ORIGINALLY
#
#
# def rate_limiting(free_limit, gold_limit, token):
# 	try:
# 		unverified_claims = jwt.get_unverified_claims(token)  # don't really need try catch if wrapper verifies token
# 	except Exception:
# 		return abort(401, message="Bearer token is invalid.")
#
# 	start = time.time()
#
# 	curr_minute = timer_minutes(0, time.time())
#
# 	key = token + ':' + str(curr_minute)
# 	memb_claim = unverified_claims.get("extension_Membership")
#
# 	try:
# 		# pipe = rc.pipeline()
# 		calls = rc.get(key)
# 	except (redis.ConnectionError, ConnectionRefusedError):
# 		return abort(408, message="Server unavailable.")
#
# 	# # pipe = rc.pipeline()
# 	# calls = rc.get(key)
#
# 	if (memb_claim is None or memb_claim == "free") and (calls is None or int(calls) < free_limit):
# 		# pipe.incr(key).expire(key, 59).execute()
# 		rc.incr(key)
# 		rc.expire(key, 59)
# 		print(int(rc.get(key)))
# 	elif memb_claim == "gold" and (calls is None or int(calls) < gold_limit):
# 		# pipe.incr(key).expire(key, 59).execute()
# 		rc.incr(key)
# 		rc.expire(key, 59)
# 		print(int(rc.get(key)))
# 	else:
# 		if memb_claim is None or memb_claim == "free":
# 			return abort(429, message="Exceeded " + str(free_limit) + " API requests per minute. Please wait to try again.")
# 		elif memb_claim == "gold":
# 			return abort(429, message="Exceeded " + str(gold_limit) + " API requests per minute. Please wait to try again.")
# 		else:
# 			return abort(401, message="No membership found. Please contact the administrator to report this issue.")
#
# 	end = time.time()
# 	print("REDIS:")
# 	print(end - start)

