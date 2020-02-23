import dash
from dash.dependencies import Input, Output, State
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol

from invest_utils import *
from invest_layout_main import app_layout
from invest_time_range import time_range_callback
from invest_forecast import forecast_table, forecast_figure
from invest_analysts import analyst_table, analyst_figure

#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = app_layout

#------------------------------------------------------------------------------
# Callback for table1
#------------------------------------------------------------------------------
@app.callback(
	[
		Output('table1', 'data'),
		Output('table1', 'columns'),
		Output('table1', 'row_selectable'),
	],
	[
		Input('tickers', 'options'),
		Input('analysis-menu', 'value'),
		Input('table1', 'selected_rows'),
	],
	[
		State('time-range', 'value'),
		State('table1', 'sort_by'),
	]
)
def update_table1(ticker_options, analysis, selected_rows, week_range, sort_by):
	if len(ticker_options)==0:
		return [],[],'single'
	tickers = [t['value'] for t in ticker_options]
	if analysis=='Forecast':
		return forecast_table(tickers, sort_by, week_range)

#------------------------------------------------------------------------------
# Callback for table2
#------------------------------------------------------------------------------
@app.callback(
	[
		Output('table2', 'data'),
		Output('table2', 'columns'),
	],
	[
		Input('table1', 'data'),
		Input('table2', 'sort_by'),
	],
	[
		State('table1', 'selected_rows'),
		State('time-range', 'value'),
		State('analysis-menu', 'value'),
	]
)
def update_table2(table1_data, table2_sort_by, table1_selected_rows, week_range, analysis):
	if not week_range or not table1_selected_rows or not table1_data:
		return [], []
	# print('update_table2', table2_sort_by, table1_selected_rows, len(table1_data))
	tickers = [table1_data[i]['Stock'] for i in table1_selected_rows]
	if analysis=='Forecast':
		return analyst_table(tickers[0], table2_sort_by, week_range)

#------------------------------------------------------------------------------
# Callback to plot figure1
#------------------------------------------------------------------------------
@app.callback(
	Output('figure1', 'figure'),
	[
		Input('table1', 'data'),
	],
	[
		State('table1', 'selected_rows'),
		State('time-range', 'value'),
		State('analysis-menu', 'value'),
	]
)
def plot_figure1(table_data, selected_rows, week_range, analysis):
	if not week_range or not selected_rows or not table_data:
		return dict(data=[],layout={})
	tickers = [table_data[i]['Stock'] for i in selected_rows]
	if analysis == 'Forecast':
		return forecast_figure(tickers[0], week_range)

#------------------------------------------------------------------------------
# Callback to plot figure2
#------------------------------------------------------------------------------
@app.callback(
	Output('figure2', 'figure'),
	[
		Input('table1', 'data'),
	],
	[
		State('table1', 'selected_rows'),
		State('time-range', 'value'),
		State('analysis-menu', 'value'),
	]
)
def plot_figure2(table1_data, table1_selected_rows, week_range, analysis):
	if not week_range or not table1_selected_rows or not table1_data:
		return dict(data=[],layout={})
	tickers = [table1_data[i]['Stock'] for i in table1_selected_rows]
	if analysis == 'Forecast':
		return analyst_figure(tickers[0], week_range)

#------------------------------------------------------------------------------
# Callback to time range slider
#------------------------------------------------------------------------------
@app.callback(
	[
		Output('time-range', 'min'),
		Output('time-range', 'value'),
		Output('time-range', 'marks'),
	],
	[ Input('time-menu', 'value')]
)
def set_time_range(months_ago):
	if months_ago is None:
		months_ago = 1
	return time_range_callback(months_ago)

#------------------------------------------------------------------------------
@app.callback(
	Output('table1', 'selected_rows'),
	[
		Input('table1', 'sort_by'),
		Input('time-range', 'value'),
	],
	[
		State('table1', 'data'),
		State('table1', 'selected_rows'),
		State('tickers', 'options'),
	]
)
def reset_table1_selected_rows(sort_by, week_range, old_data, old_selected_rows,  ticker_options):
	if not old_data:
		return []
	selected_tickers = [ old_data[i]['Stock'] for i in old_selected_rows ]
	tickers = [t['value'] for t in ticker_options]
	new_data, c, r = forecast_table(tickers, sort_by, week_range)
	rows = [ i for i in range(len(new_data)) if new_data[i]['Stock'] in selected_tickers ]
	return rows

#------------------------------------------------------------------------------
@app.callback(
	Output('portfolios-menu', 'value'),
	[ 
		Input('action-menu', 'value'),
	],
	[ 
		State('table1', 'data'),
		State('table1', 'selected_rows'),
		State('text-input', 'value'), 
		State('portfolios-menu', 'value'), 
	]
)
def action_menu_callback(action, table1_data, table1_selected_rows, text_input, portfolio_name):
	if action == 'Add symbol' and text_input.strip() != '' and portfolio_name != '':
		ticker_name = text_input.strip().upper()
		res = load_data_for_ticker(ticker_name)
		if res == False:
			print('Unable to add {}'.format(ticker_name))
			return portfolio_name
		tickers = None
		with open(os.path.join(PORTFOLIOS_DIR, portfolio_name)) as fp:
			tickers = set([ticker_name] + [ line.strip() for line in fp.readlines()])
		with open(os.path.join(PORTFOLIOS_DIR, portfolio_name), 'w') as fp:
			for t in sorted(tickers):
				fp.write(t + '\n')
		print('{} is added to {}'.format(ticker_name, portfolio_name))
		return portfolio_name

	elif action == 'Remove symbol' and len(table1_selected_rows)>0:
		with open(os.path.join(PORTFOLIOS_DIR, portfolio_name)) as fp:
			to_be_removed = [table1_data[i]['Stock'] for i in table1_selected_rows]
			tickers = set([line.strip() for line in fp.readlines()])
			for t in to_be_removed:
				tickers.remove(t)
		with open(os.path.join(PORTFOLIOS_DIR, portfolio_name), 'w') as fp:
			for t in sorted(tickers):
				fp.write(t + '\n')
		print('{} removed from {}'.format(to_be_removed, portfolio_name))
		return portfolio_name

	elif action == 'Add portfolio' and text_input.strip() != '':
		new_portfolio = text_input.strip()
		output_file = os.path.join(PORTFOLIOS_DIR, new_portfolio)
		if os.path.exists(output_file):
			print('Portfolio {} already exists.'.format(new_portfolio))
		else:
			with open(output_file, 'w') as f:
				f.write('')
		return new_portfolio

	elif action == 'Remove portfolio' and portfolio_name != '':
		to_be_removed = os.path.join(PORTFOLIOS_DIR, portfolio_name)
		if not os.path.exists(to_be_removed):
			print('Portfolio {} does not exist.'.format(portfolio_name))
		else:
			os.remove(to_be_removed)
		return ''

	elif action == 'Update portfolio' and portfolio_name != '':
		load_data_for_portfolio(portfolio_name, update=True)
		return portfolio_name

	return ''

#------------------------------------------------------------------------------
@app.callback(
	[
		Output('portfolios-menu', 'options'),
		Output('tickers', 'options'),
		Output('time-menu', 'value'),	
	],
	[
		Input('portfolios-menu', 'value'),
	]
)
def load_portfolio(name):
	# print('load_portfolio:', name)
	if name=='':
		return portfolio_list(), [], 1
	portfolio_name = name
	tickers = []
	input_file = os.path.join(PORTFOLIOS_DIR, portfolio_name)
	with open(input_file) as fp:
		tickers = [dict(label=line.strip(), value=line.strip()) for line in fp.readlines()]
	return portfolio_list(), tickers, 1

#------------------------------------------------------------------------------

if __name__ == '__main__':
	setup()
	app.run_server(debug=DEBUG)

#------------------------------------------------------------------------------
