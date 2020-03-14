from dash.dependencies import Input, Output, State
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol
import dash_html_components as html
import datetime
from invest_utils import *

#------------------------------------------------------------------------------
def main_table(tickers, start_date):
	columns = [
		{
			'name': ['','Stock'],
			'id':'Stock',
			'type':'text',
			# 'presentation':'markdown',
		},
		{
			'name': ['Rating','Score'],
			'id':'Score',
			'type':'numeric',
			'format': Format(precision=2,scheme=Scheme.fixed),
		},
		{
			'name': ['Rating','Count'],
			'id':'Count',
			'type':'numeric',
		},
		{
			'name': ['Growth Estimate', 'Qrt'],
			'id':'Quarter',
			'type':'numeric',
			'format': FormatTemplate.percentage(2).sign(Sign.positive),
		},
		{
			'name': ['Growth Estimate', 'Next Qtr'],
			'id':'NextQuarter',
			'type':'numeric',
			'format': FormatTemplate.percentage(2).sign(Sign.positive),
		},
		{
			'name': ['Growth Estimate', 'Year'],
			'id':'Year',
			'type':'numeric',
			'format': FormatTemplate.percentage(2).sign(Sign.positive),
		},
		{
			'name': ['Growth Estimate', 'Next Year'],
			'id':'NextYear',
			'type':'numeric',
			'format': FormatTemplate.percentage(2).sign(Sign.positive),
		},
	]
	data = []
	for t in tickers:
		if t not in STOCKS or t not in RATINGS:
			print('{} is not found.'.format(t))
			continue
		start = determine_start_date(start_date)
		end = datetime.datetime.today()
		stock_df = STOCKS[t][start:end]
		rating_df = RATINGS[t][start:end]
		trends = FINANCIALS[t]['trends']
		if len(stock_df) > 0 and len(rating_df):
			latest_price = stock_df.iloc[-1]['Adj Close']
			target_price = rating_df[rating_df.Price>0].Price
			if len(target_price)==0:
				min_ret, med_ret, max_ret = 0, 0, 0
			else:
				min_ret = target_price.min()/latest_price-1
				med_ret = target_price.median()/latest_price-1
				max_ret = target_price.max()/latest_price-1

			# return_at_forecast = []
			gaps = []
			for i in range(len(target_price)):
				date = target_price.index[i]
				idx = min(np.searchsorted(stock_df.index, date), len(stock_df)-1)
				price_at_forecast = stock_df.iloc[idx]['Adj Close']
				# return_at_forecast.append(target_price.iloc[i]/price_at_forecast-1)

				t_at_forecast = stock_df.index[idx]
				t_latest = stock_df.index[-1]
				p_star = price_at_forecast + (target_price.iloc[i]-price_at_forecast)*(t_latest-t_at_forecast).days/365
				gap = (latest_price - p_star)/latest_price
				gaps.append(gap)

			data.append({
				'Stock' : t,
				'Score' : rating_df[rating_df.Rating >= 0].Rating.mean(),
				'Count' : len(rating_df[rating_df.Price>0]),
				'Quarter' : trends['Growth_Quarter']/100,
				'NextQuarter' : trends['Growth_NextQuarter']/100,
				'Year' : trends['Growth_Year']/100,
				'NextYear' : trends['Growth_NextYear']/100,
			})
		else:
			Debug('No data for', t, 'within range.')

	data.sort(key=lambda c: c['Score'], reverse=True)
	return data, columns, 'single'

#------------------------------------------------------------------------------
def secondary_table(ticker, start_date):
	rating_label={0:'?',1:'Sell',2:'Hold',3:'Buy',4:'Outperform',5:'Strong Buy'}
	columns = [
		{
			'name':'Date',
			'id':'Date',
		},
		{
			'name':'Forecaster',
			'id':'Forecaster',
		},
		{
			'name':'Trust',
			'id':'Trust',
			'type':'numeric',
		},
		{
			'name':'Rating',
			'id':'Rating',
		},
		{
			'id':'Forecast',
			'name':'Forecast',
			'type':'numeric',
			'format': FormatTemplate.percentage(1).sign(Sign.positive),
		},
	]
	start = determine_start_date(start_date)
	end = datetime.datetime.today()

	stock = STOCKS[ticker]
	series = stock['Adj Close'][start:end]

	df = RATINGS[ticker][start:end]
	df = df.sort_index(ascending=False)
	data = []
	for i in range(len(df)):
		date = df.index[i]
		idx = min(np.searchsorted(series.index, date), len(series)-1)
		date_nearest = series.index[idx]
		close_price = stock['Adj Close'].loc[date_nearest]

		item = df.iloc[i]
		score = round(get_analyst_score(item.Analyst),2)
		data.append({
			'Date':datetime.datetime.strftime(item.name,'%m.%d'),
			'Forecaster':item.Analyst,
			'Trust':score,
			'Rating': rating_label[item.Rating],
			# 'Price': close_price,
			# 'Forecast':item.Price,
			'Forecast':item.Price/close_price-1,
		})
	return data, columns

#------------------------------------------------------------------------------