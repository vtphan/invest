from dash.dependencies import Input, Output, State
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol
import dash_html_components as html
import datetime
from invest_utils import *

#------------------------------------------------------------------------------
def historical_table(tickers, start_date):
	columns = [
		{
			'name':'Stock',
			'id':'Stock',
			'type':'text',
		},
		{
			'name':'Surprise 1',
			'id':'S1',
			'type':'numeric',
			'format': FormatTemplate.percentage(2).sign(Sign.positive),
		},
		{
			'name':'Surprise 2',
			'id':'S2',
			'type':'numeric',
			'format': FormatTemplate.percentage(2).sign(Sign.positive),
		},
		{
			'name':'Surprise 3',
			'id':'S3',
			'type':'numeric',
			'format': FormatTemplate.percentage(2).sign(Sign.positive),
		},
		{
			'name':'Surprise 4',
			'id':'S4',
			'type':'numeric',
			'format': FormatTemplate.percentage(2).sign(Sign.positive),
		},
		{
			'name':'Return',
			'id':'Return',
			'type':'numeric',
			'format': FormatTemplate.percentage(1).sign(Sign.positive),
		},
	]
	data = []
	for t in tickers:
		if t not in STOCKS or t not in RATINGS:
			print('{} is not found.'.format(t))
			continue
		start = determine_start_date(start_date)
		end = datetime.datetime.today()
		series = STOCKS[t][start:end]['Adj Close']
		fin = FINANCIALS[t]
		if len(fin['eps']) < 4:
			surprise = [0,0,0,0]
		else:
			surprise = [ fin['eps'].Actual.iloc[i]/fin['eps'].Est.iloc[i] - 1 for i in range(4) ]

		if len(series) > 0:
			data.append({
				'Stock' : t,
				'S1' :  surprise[3],
				'S2' :  surprise[2],
				'S3' :  surprise[1],
				'S4' :  surprise[0],
				'Return' : series.iloc[-1]/series.iloc[0] - 1,
			})
		else:
			Debug('No data for', t, 'within range.')
	data.sort(key=lambda c: c['Return'], reverse=True)
	return data, columns, 'single'

#------------------------------------------------------------------------------
def historical_figure(ticker, week_range):
	start = datetime.datetime.today() - datetime.timedelta(days=-week_range[0]*7)
	end = datetime.datetime.today() - datetime.timedelta(days=-week_range[1]*7)
	plot_data = []

	prices = STOCKS[ticker]['Adj Close'][start:end]
	plot_data.append(dict(
		x = prices.index,
		y = prices/prices.iloc[0] - 1,
		mode = 'lines',
		name = ticker,
		showlegend=True,
	))
	layout=dict(title = 'Returns')
	return dict(data=plot_data, layout=layout)

#------------------------------------------------------------------------------
def performance_figure(ticker, start_date):
	fin = FINANCIALS[ticker]
	eps = fin['eps']
	if len(eps) < 4:
		return dict(data=[],layout={})
	dates = sorted(eps.index)
	dates.insert(0, dates[0]-datetime.timedelta(days=90))
	start = dates[0]
	prices = STOCKS[ticker]['Adj Close'][start:]
	plot_data = []
	plot_data.append(dict(
		x = prices.index,
		y = prices,
		mode = 'lines',
		name = ticker,
		showlegend = False,
	))
	xs, ys = [], []
	for i in range(len(eps)):
		x = eps.index[i]
		idx = min(np.searchsorted(prices.index, x), len(prices)-1)
		date_nearest = prices.index[idx]
		y = prices.iloc[max(0,idx-1)]
		xs.append(x)
		ys.append(y)
	plot_data.append(dict(
		x = xs,
		y = ys,
		mode = 'markers',
		name = 'Quarter End',
		marker = dict(
			size = 10,
		),
		showlegend = True,
	))
	layout=dict(
		title = '{} - Last 4-Quarter Performance'.format(ticker),
	)
	return dict(data=plot_data, layout=layout)

#------------------------------------------------------------------------------
def eps_figure(ticker, start_date):
	fin = FINANCIALS[ticker]
	eps = fin['eps']
	if len(eps) < 4:
		return dict(data=[],layout={})
	# dates = sorted(eps.index)
	# dates.insert(0, dates[0]-datetime.timedelta(days=90))
	plot_data, labels, label_pos = [], [], []
	for i in range(len(eps)):
		r = eps.iloc[i].Actual/eps.iloc[i].Est - 1
		if r >= 0:
			label_pos.append('top center')
		else:
			label_pos.append('bottom center')
		labels.append('{}%'.format(round(100*r,2)))
	plot_data.append(dict(
		x = eps.index,
		y = eps.Actual,
		text = labels,
		name = 'Actual EPS',
		mode = 'markers+lines+text',
		textposition= label_pos,
		marker={
			'size': 15,
			'opacity': 0.7,
			'line': {'width': 2, 'color': 'black'}
		}
	))
	estimate = eps.Est.copy()
	estimate.loc[eps.index[-1] + datetime.timedelta(days=90)] = fin['trends'].loc['EPS_Quarter']
	estimate.loc[eps.index[-1] + datetime.timedelta(days=180)] = fin['trends'].loc['EPS_NextQuarter']
	plot_data.append(dict(
		x = estimate.index,
		y = estimate,
		name = 'Estimate EPS',
		mode = 'markers',
		marker={
			'size': 15,
			'opacity': 0.6,
			'line': {'width': 2, 'color': 'black'}
		}
	))
	max_y = max(eps.Actual.max(), estimate.max())
	max_y *= 1.1
	layout=dict(
		title = '',
		yaxis = dict(range=[0, max_y]),
		legend = dict(x=0,y=1.25,orientation='h'),
        margin={'l': 40, 'b': 20, 't': 50, 'r': 30},
		height=350,
	)
	return dict(data=plot_data, layout=layout)

#------------------------------------------------------------------------------
