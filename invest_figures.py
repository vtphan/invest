from dash.dependencies import Input, Output, State
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol
import datetime
from invest_utils import *


#------------------------------------------------------------------------------
def plot_figure1(ticker, start_date):
	start = determine_start_date(start_date)
	end = datetime.datetime.today()
	ratings = RATINGS[ticker][start:end].sort_values(by=['Price','Date'], ascending=False)
	if len(ratings) > 0:
		min_rating_date = ratings.index.min()
	else:
		min_rating_date = end
	prices = STOCKS[ticker]['Adj Close'][min_rating_date-datetime.timedelta(days=365):end]
	plot_data = []

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
				mode = 'lines',
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
		min_forecast, med_forecast, max_forecast = round(tmp[0],0), tmp[len(tmp)//2], tmp[-1]
	for i in range(len(ratings)):
		if ratings.iloc[i].Price > 0:
			x.append(ratings.index[i] + datetime.timedelta(days=365))
			p = ratings.iloc[i].Price
			y.append(p)
			label = '${}'.format(int(round(p,0)))
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

	#-----------------------------------------------------------------------
	# Plot prices
	#-----------------------------------------------------------------------
	# series = prices
	plot_data.append(dict(
		x = prices.index,
		y = prices,
		mode = 'lines',
		name = '{}% Median ROI forecast'.format(round(100*(np.median(tmp)/prices[-1]-1),1)),
		line=dict(color='black'),
		opacity=0.7,
		# line=dict(color='royalblue'),
		showlegend=True,
	))

	#-----------------------------------------------------------------------
	layout=dict(
		title = '',
		legend = dict(x=0,y=1.25,orientation='h'),
		margin={'l': 40, 'b': 20, 't': 50, 'r': 10},
		xaxis = dict(range=[prices.index[0], end+datetime.timedelta(days=365+120)]),
		height=350,
	)
	return dict(data=plot_data, layout=layout)

#------------------------------------------------------------------------------

def plot_figure2(ticker, start_date, index):
	plot_data = []
	start = determine_start_date(start_date)
	end = datetime.datetime.today()
	rating_label={0:'?',1:'Sell',2:'Hold',3:'Buy',4:'Outperform',5:'Strong Buy'}
	stock = STOCKS[ticker]
	series = stock['Adj Close'][start:end]

	#-------------------------------------------------------------------------
	# Plot stock prices
	#-------------------------------------------------------------------------
	ticker_roi = round(100*(series.iloc[-1]/series.iloc[0] - 1), 2)
	plot_data.append(dict(
		x = series.index,
		y = series,
		mode = 'lines',
		name = '{} ({}% ROI)'.format(ticker, ticker_roi),
		showlegend=True,
	))

	#-------------------------------------------------------------------------
	# Plot ratings
	#-------------------------------------------------------------------------
	ratings = RATINGS[ticker]
	x, y, hover_text, marker_color, analyst_count = [], [], [], [], []

	for date in ratings.index.unique():
		if series.index[0] <= date <= series.index[-1]:
			idx = min(np.searchsorted(series.index, date), len(series)-1)
			date_nearest = series.index[idx]
			y_coord = series.iloc[max(0,idx-1)]
			x.append(date)
			y.append(y_coord)
			if date_nearest > date:
				idx = max(0, idx-1)
				date_nearest = series.index[idx]
			close_price = stock['Adj Close'].loc[date_nearest]
			item = ratings.loc[date]
			if type(item) == pandas.Series:
				item = pandas.DataFrame([item])
			labels = []
			score = item.loc[item.Rating > 0].Rating.mean()
			marker_color.append(rating_to_color(score))
			for i in range(len(item)):
				if item.iloc[i].Price <= 0:
					target_ret = 0
				else:
					target_ret = round(100*(item.iloc[i].Price/close_price-1),1)
				analyst_score = get_analyst_score(item.iloc[i].Analyst)
				labels.append([
					item.iloc[i].Analyst, 
					int(round(100*analyst_score,0)),
					rating_label[item.iloc[i].Rating],
					item.iloc[i].Price,
					target_ret,
				])
			labels = sorted(labels, key=lambda x: x[1], reverse=True)
			labels = [ '{} s{}: {}, ${} or {}%'.format(*x) for x in labels ]
			hover_text.append('{}, {} closed at ${}<br><br>{}'.format(
				date.strftime('%B %d, %Y'), 
				ticker,
				round(close_price,2),
				'<br>'.join(labels),
			))
			analyst_count.append('{}'.format('' if len(item)==1 else len(item)))

	plot_data.append(dict(
		x = x,
		y = y,
		mode = 'markers+text',
		name = 'Ratings',
		text =  analyst_count,
		textposition= 'top center',
		hovertext = hover_text,
		hoverinfo = 'text',
		marker = {
			'size': 8,
			'color': marker_color,
	        'line': { 'width':1, 'color':['black']*len(marker_color)},
		},
		showlegend=False,
	))

	#-------------------------------------------------------------------------
	# Plot index
	#-------------------------------------------------------------------------
	if index:
		if index not in STOCKS:
			load_data_for_ticker(index)
		index_prices = STOCKS[index][start:end]['Adj Close']
		normalized_to = series.iloc[0]
		index_prices = (normalized_to / index_prices.iloc[0]) * index_prices
		index_roi = round(100*(index_prices.iloc[-1]/index_prices.iloc[0] - 1),2)
		plot_data.append(dict(
			x = index_prices.index,
			y = index_prices,
			mode = 'lines',
			name = '{} ({}% ROI)'.format(index, index_roi),
			showlegend=True,
			opacity=0.85,
			line = dict(
				color= 'firebrick' if index_roi < ticker_roi else 'apple',
				dash='solid',   # solid, dot or dash
			),
		))	

	#-------------------------------------------------------------------------
	layout=dict(
		# title = '({}) {}% ROI'.format(
		# 	ticker,
		# 	round(100*(series.iloc[-1]/series.iloc[0] - 1), 2),
		# ),
		title = '',
		legend = dict(x=0,y=1.25,orientation='h'),
		margin={'l': 40, 'b': 20, 't': 50, 'r': 40},
		height=350,
	)
	return dict(data=plot_data, layout=layout)


#------------------------------------------------------------------------------

def plot_figure3(ticker, start_date):
	fin = FINANCIALS[ticker]
	eps = fin['eps']
	if len(eps) < 4:
		return dict(data=[],layout={})
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
		},
		yaxis='y1',
	))
	estimate = eps.Est.copy()
	estimate.loc[eps.index[-1] + datetime.timedelta(days=90)] = fin['trends'].loc['EPS_Quarter']
	estimate.loc[eps.index[-1] + datetime.timedelta(days=180)] = fin['trends'].loc['EPS_NextQuarter']
	plot_data.append(dict(
		x = estimate.index,
		y = estimate,
		name = 'Estimated EPS',
		mode = 'markers',
		marker={
			'size': 15,
			'opacity': 0.6,
			'line': {'width': 2, 'color': 'black'}
		},
		yaxis='y1',
	))
	y1_max = max(eps.Actual.max(), estimate.max())
	y1_max *= 1.1
	y1_min = min(eps.Actual.min(), estimate.min())
	y1_min *= 0.9

	#-------------------------------------------------------------------------
	# Plot Quarter's Return
	#-------------------------------------------------------------------------
	dates = sorted(eps.index)
	dates.insert(0, dates[0]-datetime.timedelta(days=90))
	prices = STOCKS[ticker]['Adj Close'][dates[0] : dates[-1]]
	date_nearest = []
	for i, date in enumerate(dates):
		idx = min(np.searchsorted(prices.index, date), len(prices)-1)
		date_nearest.append(prices.index[idx])
	y2 = []
	y2_min, y2_max = None, None
	label2 = []
	for i in range(1, len(date_nearest)):
		y_cur = 100*(prices.loc[date_nearest[i]]/prices.loc[date_nearest[i-1]] - 1)
		if y2_min is None or y2_min > y_cur:
			y2_min = y_cur
		if y2_max is None or y2_max < y_cur:
			y2_max = y_cur
		label2.append('{}%'.format(round(y_cur, 1)))
		y2.append(y_cur)
	y2_max *= 5
	if y2_min < 0:
		y2_min = min(y2_min*1.5, -(y2_max-y2_min)*.2)
	plot_data.append(dict(
		x = date_nearest[1:],
		y =  y2,
		name = 'ROI',
		type = 'bar',
		text = label2,
		textposition = 'outside',
		yaxis = 'y2',
	))

	#-------------------------------------------------------------------------
	layout=dict(
		title = '',
		yaxis = dict(range=[0, y1_max], title='EPS'),
		yaxis2 = dict(range=[y2_min, y2_max], title="Quarter ROI", overlaying='y1', side='right'),
		legend = dict(x=0,y=1.25,orientation='h'),
        margin={'l': 40, 'b': 20, 't': 50, 'r': 70},
		height=350,
	)
	return dict(data=plot_data, layout=layout)

#------------------------------------------------------------------------------
