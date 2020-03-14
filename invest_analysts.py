from dash.dependencies import Input, Output, State
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol
import datetime
from invest_utils import *

#------------------------------------------------------------------------------
'''
@app.callback(
	[
		Output('table2', 'data'),
		Output('table2', 'columns'),
	],
	[
		Input('table1', 'data'),
		Input('table1', 'selected_rows'),
		Input('table2', 'sort_by'),
		Input('time-range', 'value'),
		Input('analysis-menu', 'value'),
	]
)
'''
#------------------------------------------------------------------------------
def analyst_table(ticker, start_date):
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
		# if series.index[0] <= date <= series.index[-1]:
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
	# if len(sort_by) > 0:
	# 	data = sorted(data, key=lambda c: c[sort_by[0]['column_id']], reverse=sort_by[0]['direction']=='asc')
	return data, columns

#------------------------------------------------------------------------------
'''
@app.callback(
	Output('figure2', 'figure'),
	[
		Input('table2', 'data'),
		Input('table2', 'selected_rows'),
		Input('time-range', 'value'),
		Input('analysis-menu', 'value'),
	]
)
'''
#------------------------------------------------------------------------------
def analyst_figure(ticker, start_date):
	plot_data = []
	start = determine_start_date(start_date)
	end = datetime.datetime.today()
	rating_label={0:'?',1:'Sell',2:'Hold',3:'Buy',4:'Outperform',5:'Strong Buy'}
	stock = STOCKS[ticker]
	series = stock['Adj Close'][start:end]
	plot_data.append(dict(
		x = series.index,
		y = series,
		mode = 'lines',
		name = ticker,
		showlegend=False,
	))
	ratings = RATINGS[ticker]
	x, y, hover_text, marker_color, analyst_count = [], [], [], [], []
	returns = []
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
					returns.append(item.iloc[i].Price/close_price-1)
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

	if len(returns)==0:
		layout = dict()
	else:
		layout=dict(
			title = '{}% return of investment'.format(
				round(100*(series.iloc[-1]/series.iloc[0] - 1), 2),
				# series.index[0].strftime('%m.%d.%y'),
				# series.index[-1].strftime('%m.%d.%y'),
			),
           	margin={'l': 40, 'b': 20, 't': 50, 'r': 40},
			height=350,
		)
	return dict(data=plot_data, layout=layout)
#------------------------------------------------------------------------------

