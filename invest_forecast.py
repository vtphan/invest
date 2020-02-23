from dash.dependencies import Input, Output, State
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol
import dash_html_components as html
import datetime
from invest_utils import *

'''
@app.callback(
	[
		Output('table1', 'data'),
		Output('table1', 'columns'),
		Output('table1', 'row_selectable'),
	],
	[
		Input('tickers', 'values'),
		Input('table1', 'sort_by'),
		Input('table1', 'selected_rows'),
		Input('time-range', 'value'),
		Input('analysis-menu', 'value'),
	]
)
'''
def forecast_table(tickers, sort_by, selected_rows, week_range):
	columns = [
		{
			'name':'Stock',
			'id':'Stock',
			'type':'text',
			# 'presentation':'markdown',
		},
		{
			'name':'Score',
			'id':'Score',
			'type':'numeric',
			'format': Format(precision=2,scheme=Scheme.fixed),
		},
		{
			'name':'Count',
			'id':'Count',
			'type':'numeric',
		},
		{
			'name':'Gap',
			'id':'Gap',
			'type':'numeric',
			'format': FormatTemplate.percentage(1).sign(Sign.positive),
		},
		{
			'id':'Med Ret',
			'name':'median Ret',
			'type':'numeric',
			'format': FormatTemplate.percentage(1).sign(Sign.positive),
		},
		{
			'id':'Min Ret',
			'name':'min Ret',
			'type':'numeric',
			'format': FormatTemplate.percentage(1).sign(Sign.positive),
		},
		{
			'id':'Max Ret',
			'name':'max Ret',
			'type':'numeric',
			'format': FormatTemplate.percentage(1).sign(Sign.positive),
		},
	]
	data = []
	for t in tickers:
		if t not in STOCKS or t not in RATINGS:
			print('{} is not found.'.format(t))
			continue
		start = datetime.datetime.today() - datetime.timedelta(days=-week_range[0]*7)
		end = datetime.datetime.today() - datetime.timedelta(days=-week_range[1]*7)
		stock_df = STOCKS[t][start:end]
		rating_df = RATINGS[t][start:end]
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
				# print(t)
				# print('\tp_star',p_star)
				# print('\tlaterst_price', latest_price)
				# print('\tprice_at_forecast', price_at_forecast)
				# print('\ttarget_price', target_price.iloc[i])
				# print('\tdelta_t', (t_latest-t_at_forecast).days, t_latest, t_at_forecast)

			data.append({
				'Stock' : t,
				'Score' : rating_df[rating_df.Rating >= 0].Rating.mean(),
				'Count' : len(rating_df[rating_df.Price>0]),
				'Gap' : 0 if gaps==[] else np.mean(gaps), 
				'Med Ret' : med_ret,
				'Min Ret' : min_ret,
				'Max Ret' : max_ret,
			})
		else:
			Debug('No data for', t, 'within range.')

	data.sort(key=lambda c: c['Score'], reverse=True)
	if len(sort_by) > 0:
		data = sorted(data, key=lambda c: c[sort_by[0]['column_id']], reverse=sort_by[0]['direction']=='asc')
	return data, columns, 'single'


#------------------------------------------------------------------------------
'''
@app.callback(
	Output('figure1', 'figure'),
	[
		Input('table1', 'data'),
		Input('table1', 'selected_rows'),
		Input('time-range', 'value'),
		Input('analysis-menu', 'value'),
	]
)
'''
#------------------------------------------------------------------------------
def forecast_figure(ticker, week_range):
	start = datetime.datetime.today() - datetime.timedelta(days=-week_range[0]*7)
	end = datetime.datetime.today() - datetime.timedelta(days=-week_range[1]*7)
	ratings = RATINGS[ticker][start:end].sort_values(by=['Price','Date'], ascending=False)
	if len(ratings) > 0:
		min_rating_date = ratings.index.min()
	else:
		min_rating_date = end
	prices = STOCKS[ticker]['Adj Close'][min_rating_date-datetime.timedelta(days=180):end]

	#-----------------------------------------------------------------------
	# Plot prices
	#-----------------------------------------------------------------------
	series = prices
	plot_data = []
	plot_data.append(dict(
		x = series.index,
		y = series,
		mode = 'lines',
		name = 'Price',
		showlegend=False,
	))

	#-----------------------------------------------------------------------
	# Plot markers linking dates of forecast and dates of target price
	#-----------------------------------------------------------------------
	for i in range(len(ratings)):
		if ratings.iloc[i].Price > 0:
			idx = min(np.searchsorted(prices.index, ratings.index[i]), len(prices)-1)
			date_nearest = prices.index[idx]
			y_coord = prices.iloc[max(0,idx-1)]
			x = [ratings.index[i], ratings.index[i] + datetime.timedelta(days=365)]
			y = [y_coord, ratings.iloc[i].Price]
			plot_data.append(dict(
				x = x,
				y = y,
				mode = 'lines+markers',
				size = 1,
				hoverinfo='skip',
				showlegend=False,
				marker = dict(
					size=1,
				),
				line = dict(
					width=1,
					color='rgba(117, 46, 46, 0.2)',
				),
			))

	#-----------------------------------------------------------------------
	# Plot forecast markers
	#-----------------------------------------------------------------------
	min_forecast, med_forecast, max_forecast = 0,0,0
	min_done, med_done, max_done = False, False, False
	x, y, text = [], [], []
	tmp = sorted(ratings[ratings.Price>0].Price)
	if len(tmp)>0:
		min_forecast, med_forecast, max_forecast = tmp[0], tmp[len(tmp)//2],tmp[-1]
	# if len(ratings[ratings.Price>0]) > 0:
	# 	min_forecast = np.min(ratings[ratings.Price>0].Price)
	# 	med_forecast = np.median(ratings[ratings.Price>0].Price)
	# 	max_forecast = np.max(ratings[ratings.Price>0].Price)
	for i in range(len(ratings)):
		if ratings.iloc[i].Price > 0:
			x.append(ratings.index[i] + datetime.timedelta(days=365))
			p = ratings.iloc[i].Price
			y.append(p)
			label = '${}'.format(p)
			if not min_done and p==min_forecast:
				text.append(label)
				min_done = True
			elif not med_done and p==med_forecast:
				text.append(label)
				med_done = True
			elif not max_done and p==max_forecast:
				text.append(label)
				max_done = True
			else:
				text.append('')

	plot_data.append(dict(
		x = x,
		y = y,
		mode = 'markers+text',
		name = 'Forecast',
		marker=dict(
			color = '#4f4949'
		),
		textposition= 'right center',
		text = text,
		showlegend=False,
	))
	layout=dict(title = '{} - Median return at closing (${}) on {}: {}%'.format(
		ticker,
		round(prices[-1],2), 
		prices.index[-1].strftime('%m.%d'),
		round(100*(np.median(tmp)/prices[-1]-1),1)))
	return dict(data=plot_data, layout=layout)

