import datetime
import re
import os
import requests
import numpy as np
from bs4 import BeautifulSoup
import pandas
import pandas_datareader as pdr
from yahoo_fin.stock_info import get_analysts_info
import holidays

#------------------------------------------------------------------------------

DEBUG = True

#------------------------------------------------------------------------------

PORTFOLIOS_DIR = './Portfolios'
STOCKS_DIR = './Stocks'
RATINGS_DIR = './Ratings'
INFO_DIR = './Info'
INDEX_FILE = './Info/index.txt'

#------------------------------------------------------------------------------
# Global dataframes. Loaded once.
#------------------------------------------------------------------------------

STOCKS = {}
RATINGS = {}
FINANCIALS = {}
QUOTES = {}
ANALYSTS = None

BadAnalysts = ['cfra']

#------------------------------------------------------------------------------

def Debug(*s):
	if DEBUG:
		print(*s)

#------------------------------------------------------------------------------

VeteransDay = datetime.date(datetime.date.today().year, 11, 11)
Holidays = holidays.UnitedStates(years=datetime.date.today().year, state='DE')
Holidays = { k:v for k,v in Holidays.items() if k != VeteransDay }

#------------------------------------------------------------------------------
def setup(update=False):
	if not os.path.exists(INFO_DIR):
		os.mkdir(INFO_DIR)
	if not os.path.exists(PORTFOLIOS_DIR):
		os.mkdir(PORTFOLIOS_DIR)
	if not os.path.exists(STOCKS_DIR):
		os.mkdir(STOCKS_DIR)
	if not os.path.exists(RATINGS_DIR):
		os.mkdir(RATINGS_DIR)

	load_analyst_data()
	tickers = set()
	for portfolio in os.listdir(PORTFOLIOS_DIR):
		for t in open(os.path.join(PORTFOLIOS_DIR,portfolio)).readlines():
			t = t.strip()
			if t:
				tickers.add(t)
	tickers = sorted(tickers)
	if update:
		for t in tickers:
			load_data_for_ticker(t)
	else:
		global STOCKS, RATINGS, FINANCIALS, QUOTES
		for t in tickers:
			print('Reading information for {}: '.format(t), end='')
			try:
				print('prices, ', end='')
				stock_file = os.path.join(STOCKS_DIR, t+'.csv')
				STOCKS[t] = pandas.read_csv(stock_file, index_col='Date', parse_dates=['Date'])
			except:
				raise Exception('Problem loading prices.')

			try:
				print('ratings, ', end='')
				rating_file = os.path.join(RATINGS_DIR, t + '.csv')
				RATINGS[t] = pandas.read_csv(rating_file, index_col='Date', parse_dates=['Date'])
			except:
				raise Exception('Problem loading ratings.')

			try:
				print('financials, ', end='')
				eps_history_file = os.path.join(INFO_DIR, 'eps_history.csv')
				trends_file = os.path.join(INFO_DIR, 'trends.csv')
				earnings_df = pandas.read_csv(eps_history_file, index_col=['Ticker','Date'], parse_dates=['Date'])
				trends_df = pandas.read_csv(trends_file, index_col=['Ticker'], parse_dates=['Date'])
				FINANCIALS[t] = dict(
					eps = earnings_df.loc[(t,)][0:4],
					trends = trends_df.loc[t]
				)
			except:
				raise Exception('Problem loading financial info.')

			try:
				print('quotes')
				quote_file = os.path.join(INFO_DIR, 'quote.csv')
				QUOTES[t] = pandas.read_csv(quote_file, index_col=['Ticker']).loc[t]
			except:
				raise Exception('Problem loading quote.')

#------------------------------------------------------------------------------
def str_to_num(m):
	value = 1
	if m.endswith('T'):
		value = 10**3 * float(m.replace('T',''))
	elif m.endswith('B'):
		value = float(m.replace('B',''))
	elif m.endswith('M'):
		value = 0.001 * float(m.replace('M',''))
	else:
		raise Exception('Unknown market cap {}'.format(m))
	return value

#------------------------------------------------------------------------------
def get_company_data(ticker):
	url='http://finance.yahoo.com/quote/{}?p={}'.format(ticker,ticker)
	saved_to = os.path.join(INFO_DIR, 'quote.csv')
	if not os.path.exists(saved_to):
		print('Download company data for', ticker)
		df = pandas.read_html(url)
		df = df[1].rename(columns={1:ticker}).set_index(0).transpose()
		df.index.name = 'Ticker'
		df['Date'] = datetime.datetime.now()
		df.to_csv(saved_to)
		return df
	else:
		existing = pandas.read_csv(saved_to, index_col=['Ticker'])
		flag = False
		if ticker not in existing.index:
			flag = True
		else:
			date = pandas.to_datetime(existing.loc[ticker].Date)
			if date < datetime.datetime.today() - datetime.timedelta(days=7):
				flag = True
		if flag:
			print('Download company data for', ticker)
			df = pandas.read_html(url)
			df = df[1].rename(columns={1:ticker}).set_index(0).transpose()
			df.index.name = 'Ticker'
			df['Date'] = datetime.datetime.now()
			existing.loc[ticker, :] = df.iloc[0]
			existing.sort_index(inplace=True)
			existing.to_csv(saved_to)
		else:
			print('Data for {} already exists.'.format(ticker))
		return existing.loc[ticker]

#------------------------------------------------------------------------------
def load_data_for_portfolio(portfolio):
	path = os.path.join(PORTFOLIOS_DIR, portfolio)
	with open(path) as f:
		tickers = [ t.strip() for t in f.readlines() ]
	to_be_deleted = []
	for t in tickers:
		res = load_data_for_ticker(t)
		if res == False:
			to_be_deleted.append(t)
	for t in to_be_deleted:
		tickers.remove(t)
	with open(path, 'w') as f:
		for t in tickers:
			f.write('{}\n'.format(t))

#------------------------------------------------------------------------------
def load_data_for_ticker(ticker):
	global STOCKS, RATINGS, FINANCIALS, QUOTES
	df = get_stock_prices(ticker)
	if df is not None:
		STOCKS[ticker] = df
		RATINGS[ticker] = get_stock_ratings(ticker)
		FINANCIALS[ticker] = get_financial_info(ticker)
		QUOTES[ticker] = get_company_data(ticker)
		return True
	else:
		print('Unable to load data for ticker', ticker)
		return False

#------------------------------------------------------------------------------
def load_analyst_data():
	global ANALYSTS
	analyst_file = os.path.join(INFO_DIR, 'analysts.csv')
	ANALYSTS = pandas.read_csv(analyst_file, index_col='Brokerage', parse_dates=['Date'])

#------------------------------------------------------------------------------
# determine if file_name has been updated (modified) after the market is last closed.
#------------------------------------------------------------------------------
def need_refresh(file_name):
	def last_close():
		d = datetime.date.today()
		while d.weekday() in [5,6] or d in Holidays:
			d -= datetime.timedelta(days=1)
		time_diff = datetime.datetime.utcnow() - datetime.timedelta(hours=4) - datetime.datetime.now()
		hour_diff = round(time_diff.total_seconds()/3600)
		return datetime.datetime(d.year, d.month, d.day, 16+hour_diff)

	if not os.path.exists(file_name):
		return True
	
	mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_name))
	# Debug('need_refresh', file_name, mtime, last_close())
	if (datetime.datetime.now() - mtime).total_seconds() < 60*60:
		return False
	return mtime < last_close()

#------------------------------------------------------------------------------
def get_financial_info(ticker):
	eps_history_file = os.path.join(INFO_DIR, 'eps_history.csv')
	trends_file = os.path.join(INFO_DIR, 'trends.csv')
	if not os.path.exists(eps_history_file):
		with open(eps_history_file, 'w') as f:
			f.write('Ticker,Date,Est,Actual\n')
	if not os.path.exists(trends_file):
		with open(trends_file, 'w') as f:
			f.write('Ticker,EPS_Quarter,EPS_NextQuarter,EPS_Year,EPS_NextYear,Growth_Quarter,Growth_NextQuarter,Growth_Year,Growth_NextYear,Date\n')
	earnings_df = pandas.read_csv(eps_history_file, index_col=['Ticker','Date'], parse_dates=['Date'])
	trends_df = pandas.read_csv(trends_file, index_col=['Ticker'], parse_dates=['Date'])

	if ticker not in earnings_df.index:
		ignore = False
		try:
			Debug('Update financial info for', ticker)
			info = get_analysts_info(ticker)
			if ('Earnings Estimate' in info) and ('EPS Trend' in info) and ('Growth Estimates' in info):
				eps_history = info['Earnings History']
				for c in eps_history.columns[1:]:
					earnings_df.loc[(ticker, pandas.to_datetime(c)), : ] = [
						float(eps_history[c].iloc[0]), 
						float(eps_history[c].iloc[1])]

				eps_trend = info['EPS Trend']
				growth = info['Growth Estimates']
				values = list(eps_trend.iloc[0][1:].values)
				for i in range(4):
					if pandas.isnull(growth.iloc[i][1]):
						values.append(0)
					else:
						values.append(float(growth.iloc[i][1].strip('%').replace(',','')))
				values.append(datetime.datetime.today())
				trends_df.loc[ticker, :] = values
			else:
				ignore = True
		except:
			ignore = True

		if ignore:
			earnings_df.loc[(ticker, pandas.to_datetime('1975-01-01')), : ] = [0,0]
			trends_df.loc[ticker, :] = [0,0,0,0,0,0,0,0,datetime.datetime.today()]
		earnings_df.sort_index(inplace=True)
		earnings_df.to_csv(eps_history_file)
		trends_df.sort_index(inplace=True)
		trends_df.to_csv(trends_file)

	earnings_df = pandas.read_csv(eps_history_file, index_col=['Ticker','Date'], parse_dates=['Date'])
	trends_df = pandas.read_csv(trends_file, index_col=['Ticker'], parse_dates=['Date'])
	result = dict(
		eps = earnings_df.loc[(ticker,)][0:4],
		trends = trends_df.loc[ticker]
	)
	return result

#------------------------------------------------------------------------------
def get_stock_prices(stock, start=datetime.date(2015,1,1)):
	try:
		saved_file = os.path.join(STOCKS_DIR, stock+'.csv')
		Debug('Reading stock prices from', saved_file)
		if need_refresh(saved_file):
			pdr.get_data_yahoo(stock, start=start).to_csv(saved_file)
		df = pandas.read_csv(saved_file, index_col='Date', parse_dates=['Date'])
		return df
	except:
		return None

#------------------------------------------------------------------------------
def get_stock_ratings(stock):
	try:
		rating_file = os.path.join(RATINGS_DIR, stock + '.csv')
		Debug('Reading stock ratings from', rating_file)
		if need_refresh(rating_file):
			download_stock_ratings(stock)
		df = pandas.read_csv(rating_file, index_col='Date', parse_dates=['Date'])
		return df
	except:
		return None

#------------------------------------------------------------------------------
def download_stock_ratings(ticker):
	info_file = os.path.join(INFO_DIR,'urls.csv')
	info_df = pandas.read_csv(info_file, index_col='Ticker')
	if ticker not in info_df.index:
		url_root = get_url_root(ticker)
		info_df.loc[ticker] = url_root
		info_df.to_csv(info_file)
	else:
		url_root = info_df.loc[ticker]['Url']

	ticker_file = os.path.join(RATINGS_DIR, ticker+'.csv')
	if not os.path.exists(ticker_file):
		with open(ticker_file, 'w') as fp:
			fp.write('Date,Analyst,Rating,Price\n')
	ticker_df = pandas.read_csv(ticker_file, index_col=['Date','Analyst'], parse_dates=['Date'])

	print('Retrieving data for', ticker)
	rating_url = url_root + 'price-target/'
	page = requests.get(rating_url)
	if page.status_code == 200:
		soup = BeautifulSoup(page.text, 'html.parser')
		tables = soup.find_all('table')
		if len(tables) >=2:
			rows = tables[1].find_all('tr')
			for i in range(1, len(rows)):
				items = rows[i].find_all('td')
				if len(items) >= 5:
					date = pandas.to_datetime(items[0].text)
					analyst = items[1].text
					rating = items[3].get('data-sort-value')
					target_price = items[4].get('data-sort-value')
					if (date, analyst) not in ticker_df.index:
						ticker_df.loc[(date, analyst), : ] = [rating,target_price]
	ticker_df.sort_index(inplace=True)
	ticker_df.to_csv(ticker_file)
	return True

#------------------------------------------------------------------------------
def get_url_root(ticker):
    url_root = 'https://www.marketbeat.com/stocks/NASDAQ/'
    url = url_root + ticker + '/'
    page = requests.get(url)
    if page.url == url:
        return url_root + ticker + '/'
    else:
        exchange = page.url.split('/')[-3]
        return 'https://www.marketbeat.com/stocks/{}/{}/'.format(exchange,ticker)
        
#------------------------------------------------------------------------------
def rating_to_color(rating):
	if rating >= 3.5:
		return '#02f748'
	if rating >= 3.0:
		return '#89f702'
	if rating >= 2.5:
		return '#f7be02'
	if rating >= 2.0:
		return '#f78902'
	if rating >= 1.7:
		return '#f76002'
	if rating == 0:
		return '#eee'
	return '#f70202'

#------------------------------------------------------------------------------
def determine_start_date(start_date):
	if len(STOCKS) < 1:
		return None
	dates = STOCKS[ list(STOCKS.keys())[0] ].index
	return dates[-7*start_date]
	# if start_date == '1W':
	# 	return dates[-5]
	# if start_date == '2W':
	# 	return dates[-10]
	# if start_date == '3W':
	# 	return dates[-16]
	# if start_date == '1M':
	# 	return dates[-22]
	# if start_date == '1.5M':
	# 	return dates[-33]
	# if start_date == '2M':
	# 	return dates[-22*2]
	# if start_date == '3M':
	# 	return dates[-22*3]
	# if start_date == '3M':
	# 	return dates[-22*4]
	# if start_date == '6M':
	# 	return dates[-22*6]
	# if start_date == '9M':
	# 	return dates[-22*9]
	# if start_date == '1Y':
	# 	return dates[-253]
	# if start_date == '1.5Y':
	# 	return dates[-380]
	# if start_date == '2Y':
	# 	return dates[-253*2]
	# if start_date == '3Y':
	# 	return dates[-253*3]
	# if start_date == '3Y':
	# 	return dates[-253*4]
	# return None

#------------------------------------------------------------------------------
def portfolio_list():
	saved_file = os.path.join(PORTFOLIOS_DIR, '__SAVED__')
	if not os.path.exists(saved_file):
		with open(saved_file,'w') as f:
			f.write('')
	return [dict(label=p, value=p) for p in sorted(os.listdir(PORTFOLIOS_DIR))]

#------------------------------------------------------------------------------
def index_list():
	if not os.path.exists(INDEX_FILE):
		with open(INDEX_FILE,'w') as f:
			f.write('')
	return [dict(label=line.strip(), value=line.strip()) for line in sorted(open(INDEX_FILE).readlines()) ]

#------------------------------------------------------------------------------

def get_analyst_score(brokerage):
	global ANALYSTS, BadAnalysts

	# key = brokerage.lower().replace('.','').replace('& ','').replace(' ','-')
	# key = brokerage.lower().replace('"','').replace('.','').replace('& ','').replace(', ','-').replace(' ','-')
	key = brokerage.lower().replace('"','').replace("'",'').replace('.','').replace('& ','').replace('&','').replace(', ','-').replace(' ','-')
	if key in BadAnalysts:
		return 0

	if key not in ANALYSTS.index:
		analyst_file = os.path.join(INFO_DIR, 'analysts.csv')
		add_brokerage(key, analyst_file)
		ANALYSTS = pandas.read_csv(analyst_file, index_col='Brokerage', parse_dates=['Date'])

	if key in ANALYSTS.index:
		item = ANALYSTS.loc[key]
		return item.Good / (item.Good+item.Bad)
	else:
		return 0

#------------------------------------------------------------------------------------
def add_brokerage(brokerage, info_file='./Info/analysts.csv'):
	url='https://www.marketbeat.com/ratings/by-issuer/{}-stock-recommendations/'.format(brokerage)
	page = requests.get(url)
	if page.status_code == 200:
		soup = BeautifulSoup(page.text, 'html.parser')
		tds = soup.find_all('table')[1].find_all('td')
		better_than_sp500 = float(tds[5].text.split(' ')[0].replace(',',''))
		worse_than_sp500 = float(tds[8].text.split(' ')[0].replace(',',''))

		if not os.path.exists(info_file):
			with open(info_file, 'w') as fp:
				fp.write('Brokerage,Good,Bad,Date\n')
		brokerage_df = pandas.read_csv(info_file, index_col='Brokerage', parse_dates=['Date'])
		brokerage_df.loc[brokerage] = [better_than_sp500, worse_than_sp500, datetime.datetime.today()]
		brokerage_df.sort_index(inplace=True)
		brokerage_df.to_csv(info_file)
		print('Saving info of {} to {}'.format(brokerage, info_file))
		return True
	else:
		print('Unable to extract information for {}'.format(brokerage))
		return False

#------------------------------------------------------------------------------------

