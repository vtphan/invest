import dash_core_components as dcc 
import dash_html_components as html 
from invest_utils import portfolio_list

#----------------------------------------------------------------------
text_input = html.Div(
	dcc.Input(id='text-input', type='text', value='', placeholder='INPUT'),
	className = 'two columns',
)

#----------------------------------------------------------------------
portfolios_menu = html.Div(
	dcc.Loading(
		id='loading',
		type='dot',
		fullscreen=False,
		children=[
			dcc.Dropdown(
				id = 'portfolios-menu', 
				options = [],
				value = '',
				clearable = False,
				placeholder='PORTFOLIO',
			)]),
	className = 'two columns',
)

#----------------------------------------------------------------------
action_menu = html.Div(
		dcc.Dropdown(
			id = 'action-menu', 
			options=[
				{'label':'Compare symbol', 'value':'Compare symbol'},
				{'label':'Add symbol', 'value':'Add symbol'},
				{'label':'Save symbol(s)', 'value':'Save symbols'},
				{'label':'Remove symbol(s)', 'value':'Remove symbols'},
				{'label':'Add portfolio', 'value':'Add portfolio'},
				{'label':'Remove portfolio', 'value':'Remove portfolio'},
				{'label':'Update portfolio data', 'value':'Update portfolio'},
			], 
			value = '', 
			clearable=True,
			placeholder='ACTION'),
	className = 'two columns',
)

#----------------------------------------------------------------------
time_menu =	html.Div(
	dcc.RadioItems(id='time-menu', 
		options = [
			{'label':'1W','value':'1W'},
			{'label':'1M','value':'1M'},
			{'label':'2M','value':'2M'},
			{'label':'3M','value':'3M'},
			{'label':'6M','value':'6M'},
			{'label':'1Y','value':'1Y'},
			{'label':'2Y','value':'2Y'},
			{'label':'3Y','value':'3Y'},
		],
		value='1W',
        labelStyle={'display': 'inline-block'},
	), 
	className = 'six columns',
)

#----------------------------------------------------------------------
analysis_menu =html.Div(
	dcc.Dropdown(id='analysis-menu', 
		options = [
			{'label':'Forecast','value':'Forecast'},
			{'label':'Finance','value':'Finance'},
			{'label':'Trade','value':'Trade'},
		],
		value = 'Trade',
		clearable = False,
	), 
	className = 'two columns',
)

#----------------------------------------------------------------------
visualization_menu = html.Div(
	dcc.Dropdown(id='visualization-menu', 
		options = [],
		value = '',
		clearable = False,
	), 
	className = 'two columns',
)

