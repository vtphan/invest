from dash.dependencies import Input, Output, State
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol
import dash_html_components as html
import plotly.graph_objs as go
import datetime
from invest_utils import *

#------------------------------------------------------------------------------
def trade_table(tickers, week_range):
	columns = [
		{
			'name':'Stock',
			'id':'Stock',
			'type':'text',
		},
		{
			'name':'Return',
			'id':'Return',
			'type':'numeric',
			'format': FormatTemplate.percentage(1).sign(Sign.positive),
		},
		{
			'name':'Average',
			'id':'Average',
			'type':'numeric',
			'format': FormatTemplate.money(2),
		},
		{
			'name':'Std',
			'id':'Std',
			'type':'numeric',
			'format': FormatTemplate.money(2),
		},
		{
			'name':'Low',
			'id':'Low',
			'type':'numeric',
			'format': FormatTemplate.money(2),
		},
		{
			'name':'High',
			'id':'High',
			'type':'numeric',
			'format': FormatTemplate.money(2),
		},
	]
	data = []
	for t in tickers:
		if t not in STOCKS or t not in RATINGS:
			print('{} is not found.'.format(t))
			continue
		start = datetime.datetime.today() - datetime.timedelta(days=-week_range[0]*7)
		end = datetime.datetime.today() - datetime.timedelta(days=-week_range[1]*7)
		series = STOCKS[t][start:end]
		if len(series) > 0:
			data.append({
				'Stock' : t,
				'Return' :  series['Adj Close'].iloc[-1]/series['Adj Close'].iloc[0] - 1,
				'Average' :  series['Adj Close'].mean(),
				'Std' :  series['Adj Close'].std(),
				'Low' :  series['Low'].min(),
				'High' : series['High'].max(),
			})
		else:
			Debug('No data for', t, 'within range.')
	data.sort(key=lambda c: c['Return'], reverse=True)
	return data, columns, 'single'

#------------------------------------------------------------------------------
def trade_figure1(ticker, week_range):
	start = datetime.datetime.today() - datetime.timedelta(days=-week_range[0]*7)
	end = datetime.datetime.today() - datetime.timedelta(days=-week_range[1]*7)
	plot_data = []

	prices = STOCKS[ticker][start:end]
	plot_data.append(go.Ohlc(
		x = prices.index,
		open = prices.Open,
		close = prices.Close,
		high = prices.High,
		low = prices.Low,
		name = ticker,
		# showlegend=True,
	))
	layout=dict(
		title = 'OHLC',
		xaxis = dict(rangeslider=dict(visible=False)),
	)
	return dict(data=plot_data, layout=layout)

#------------------------------------------------------------------------------

