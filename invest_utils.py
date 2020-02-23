import datetime
import re
import os
import requests
import numpy as np
from bs4 import BeautifulSoup
import pandas
import pandas_datareader as pdr

#------------------------------------------------------------------------------

PORTFOLIOS_DIR = './Portfolios'
STOCKS_DIR = './Stocks'
RATINGS_DIR = './Ratings'
INFO_DIR = './Info'

#------------------------------------------------------------------------------
# Global dataframes. Loaded once.
#------------------------------------------------------------------------------

STOCKS = {}
RATINGS = {}
ANALYSTS = None

BadAnalysts = ['cfra']

#------------------------------------------------------------------------------
def setup(update=False):
	load_analyst_data()
	for portfolio in os.listdir(PORTFOLIOS_DIR):
		load_data_for_portfolio(portfolio, update)
	
#------------------------------------------------------------------------------
def load_data_for_portfolio(portfolio, update=False):
	path = os.path.join(PORTFOLIOS_DIR, portfolio)
	with open(path) as f:
		tickers = [ t.strip() for t in f.readlines() ]
	to_be_deleted = []
	for t in tickers:
		res = load_data_for_ticker(t, update)
		if res == False:
			to_be_deleted.append(t)
	for t in to_be_deleted:
		tickers.remove(t)
	with open(path, 'w') as f:
		for t in tickers:
			f.write('{}\n'.format(t))

#------------------------------------------------------------------------------
def load_data_for_ticker(ticker, update=False):
	global STOCKS, RATINGS
	df = get_stock_prices(ticker, update=update)
	if df is not None:
		STOCKS[ticker] = df
		RATINGS[ticker] = get_stock_ratings(ticker, update=update)
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
def get_stock_prices(stock, days=365*5, update=False):
	try:
		saved_file = os.path.join(STOCKS_DIR, stock+'.csv')
		if update or not os.path.exists(saved_file):
			today = datetime.datetime.today()
			start = today - datetime.timedelta(days=days)
			df = pdr.get_data_yahoo(stock, start=start, end=today)
			df.to_csv(saved_file)
		df = pandas.read_csv(saved_file, index_col='Date', parse_dates=['Date'])
		print('Reading stock prices from', saved_file)
		return df
	except:
		return None

#------------------------------------------------------------------------------
def get_stock_ratings(stock, update=False):
	rating_file = os.path.join(RATINGS_DIR, stock + '.csv')
	if update or not os.path.exists(rating_file):
		download_stock_ratings(stock)
	print('Reading stock ratings from', rating_file)
	df = pandas.read_csv(rating_file, index_col='Date', parse_dates=['Date'])
	return df


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

	print('Retrieving data for', ticker, '... ', end='' )
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

def portfolio_list():
	return [dict(label=p, value=p) for p in os.listdir(PORTFOLIOS_DIR)]

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

