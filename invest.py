import dash
from dash.dependencies import Input, Output, State
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol

from invest_utils import *
from invest_layout import app_layout
from invest_time_range import time_range_callback
from invest_tables import main_table, secondary_table
from invest_figures import plot_figure1, plot_figure2, plot_figure3

#------------------------------------------------------------------------------
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = app_layout

#------------------------------------------------------------------------------
def build_main_table(ticker_options, start_date):
	tickers = [t['value'] for t in ticker_options]
	data, columns, row_selectable = main_table(tickers, start_date)
	return data, columns, row_selectable

#------------------------------------------------------------------------------
@app.callback(
	Output('main-table', 'selected_rows'),
	[
		Input('date-picker', 'date'),
		# Input('time-menu', 'value'),
		Input('tickers', 'options'),
	],
	[
		State('main-table', 'data'),
		State('main-table', 'selected_rows'),
	]
)
def update_main_table_selected_rows(start_date, ticker_options, old_data, old_selected_rows):
	if not old_data:
		return []
	selected_tickers = [ old_data[i]['Stock'] for i in old_selected_rows ]
	new_data, c, r = build_main_table(ticker_options, start_date)
	rows = [ i for i in range(len(new_data)) if new_data[i]['Stock'] in selected_tickers ]
	return rows

#------------------------------------------------------------------------------
# Callback for main-table
#------------------------------------------------------------------------------
@app.callback(
	[
		Output('main-table', 'data'),
		Output('main-table', 'columns'),
		Output('main-table', 'row_selectable'),
	],
	[
		Input('main-table', 'selected_rows'),
	],
	[
		State('date-picker', 'date'),
		# State('time-menu', 'value'),
		State('tickers', 'options'),
	]
)
def main_table_callback(selected_rows, start_date, ticker_options):
	if len(ticker_options)==0:
		return [],[],'single'
	return build_main_table(ticker_options, start_date)

#------------------------------------------------------------------------------
@app.callback(
	[
		Output('secondary-table', 'data'),
		Output('secondary-table', 'columns'),
	],
	[
		Input('main-table', 'data'),
	],
	[
		State('main-table', 'selected_rows'),
		State('date-picker', 'date'),
		# State('time-menu', 'value'),
		# State('analysis-menu', 'value'),
	]
)
def secondary_table_callback(data, selected_rows, start_date):
	if not start_date or not selected_rows or not data:
		return [], []
	tickers = [data[i]['Stock'] for i in selected_rows]
	return secondary_table(tickers[0], start_date)

#------------------------------------------------------------------------------
@app.callback(
	Output('figure1', 'figure'),
	[
		Input('main-table', 'data'),
		Input('index-menu', 'value'),
	],
	[
		State('main-table', 'selected_rows'),
		State('date-picker', 'date'),
		# State('time-menu', 'value'),
	]
)
def figure1_callback(data, index, selected_rows, start_date):
	if not start_date or not selected_rows or not data:
		return dict(data=[],layout={})
	tickers = [data[i]['Stock'] for i in selected_rows]
	return plot_figure1(tickers[0], start_date, index)
	# return dict(data=[])

#------------------------------------------------------------------------------
@app.callback(
	Output('figure2', 'figure'),
	[
		Input('main-table', 'data'),
	],
	[
		State('main-table', 'selected_rows'),
		State('date-picker', 'date'),
		# State('time-menu', 'value'),
	]
)
def figure2_callback(table_data, selected_rows, start_date):
	if not start_date or not selected_rows or not table_data:
		return dict(data=[],layout={})
	tickers = [table_data[i]['Stock'] for i in selected_rows]
	return plot_figure2(tickers[0], start_date)

#------------------------------------------------------------------------------
@app.callback(
	Output('figure3', 'figure'),
	[
		Input('main-table', 'data'),
	],
	[
		State('main-table', 'selected_rows'),
		State('date-picker', 'date'),
		# State('time-menu', 'value')
	]
)
def figure3_callback(data, selected_rows, start_date):
	if not start_date or not selected_rows or not data:
		return dict(data=[],layout={})
	tickers = [data[i]['Stock'] for i in selected_rows]
	return plot_figure3(tickers[0], start_date)

#------------------------------------------------------------------------------
@app.callback(
	[
		Output('portfolios-menu', 'options'),
		Output('tickers', 'options'),
	],
	[
		Input('portfolios-menu', 'value'),
	]
)
def load_portfolio(name):
	if name=='':
		return portfolio_list(), []
	portfolio_name = name
	tickers = []
	input_file = os.path.join(PORTFOLIOS_DIR, portfolio_name)
	with open(input_file) as fp:
		tickers = [dict(label=line.strip(), value=line.strip()) for line in fp.readlines()]
	return portfolio_list(), tickers

#------------------------------------------------------------------------------
@app.callback(
	[
		Output('portfolios-menu', 'value'),
		Output('index-menu', 'options'),
	],
	[ 
		Input('action-menu', 'value'),
	],
	[ 
		State('main-table', 'data'),
		State('main-table', 'selected_rows'),
		State('text-input', 'value'), 
		State('portfolios-menu', 'value'), 
		State('index-menu', 'value'),
	]
)
def action_menu_callback(action, data, selected_rows, text_input, portfolio_name, index):
	if action == 'Add symbol' and text_input.strip() != '' and portfolio_name != '':
		ticker_name = text_input.strip().upper()
		res = load_data_for_ticker(ticker_name)
		if res == False:
			print('Unable to add {}'.format(ticker_name))
			return portfolio_name, index_list()
		tickers = None
		with open(os.path.join(PORTFOLIOS_DIR, portfolio_name)) as fp:
			tickers = set([ticker_name] + [ line.strip() for line in fp.readlines()])
		with open(os.path.join(PORTFOLIOS_DIR, portfolio_name), 'w') as fp:
			for t in sorted(tickers):
				fp.write(t + '\n')
		print('{} is added to {}'.format(ticker_name, portfolio_name))

	elif action == 'Save symbol' and len(selected_rows)>0:
		with open(os.path.join(PORTFOLIOS_DIR, '__SAVED__')) as fp:
			to_be_saved = [data[i]['Stock'] for i in selected_rows]
			tickers = set([line.strip() for line in fp.readlines()])
			for t in to_be_saved:
				tickers.add(t)
		with open(os.path.join(PORTFOLIOS_DIR, '__SAVED__'), 'w') as fp:
			for t in sorted(tickers):
				fp.write(t + '\n')
		print('{} saved to __SAVED__'.format(to_be_saved))

	elif action == 'Remove symbol' and len(selected_rows)>0:
		with open(os.path.join(PORTFOLIOS_DIR, portfolio_name)) as fp:
			to_be_removed = [data[i]['Stock'] for i in selected_rows]
			tickers = set([line.strip() for line in fp.readlines()])
			for t in to_be_removed:
				tickers.remove(t)
		with open(os.path.join(PORTFOLIOS_DIR, portfolio_name), 'w') as fp:
			for t in sorted(tickers):
				fp.write(t + '\n')
		print('{} removed from {}'.format(to_be_removed, portfolio_name))

	elif action == 'Add index' and text_input.strip() != '':
		ticker_name = text_input.strip().upper()
		with open(INDEX_FILE, 'a+') as f:
			f.write('{}\n'.format(ticker_name))
		Debug('{} is added to {}.'.format(ticker_name, INDEX_FILE))

	elif action == 'Remove index' and index != '':
		indexes = [ line.strip() for line in open(INDEX_FILE).readlines() ]
		indexes.remove(index)
		with open(INDEX_FILE, 'w') as f:
			for idx in indexes:
				f.write('{}\n'.format(idx))

	elif action == 'Add portfolio' and text_input.strip() != '':
		new_portfolio = text_input.strip()
		output_file = os.path.join(PORTFOLIOS_DIR, new_portfolio)
		if os.path.exists(output_file):
			print('Portfolio {} already exists.'.format(new_portfolio))
		else:
			with open(output_file, 'w') as f:
				f.write('')
		return new_portfolio, index_list()

	elif action == 'Remove portfolio' and portfolio_name != '':
		to_be_removed = os.path.join(PORTFOLIOS_DIR, portfolio_name)
		if not os.path.exists(to_be_removed):
			print('Portfolio {} does not exist.'.format(portfolio_name))
		else:
			os.remove(to_be_removed)
		return '', index_list()

	elif action == 'Update portfolio' and portfolio_name != '':
		load_data_for_portfolio(portfolio_name)

	return portfolio_name, index_list()

#------------------------------------------------------------------------------

if __name__ == '__main__':
	import sys
	if len(sys.argv) == 1:
		setup(update=False)
	elif sys.argv[1] == '-update':
		setup(update=True)
	else:
		print('Incorrect number of arguments. Optional parameters:')
		print('\t-update\t\tUpdate data for all stocks.')
		sys.exit(1)
	app.run_server(debug=DEBUG)

#------------------------------------------------------------------------------
