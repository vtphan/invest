import dash_core_components as dcc 
import dash_html_components as html 
from invest_utils import portfolio_list

#----------------------------------------------------------------------
text_input = html.Div(
	dcc.Input(id='text-input', type='text', value='', placeholder='Symbol or portfolio'),
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
				placeholder='Select a portfolio',
			)]),
	className = 'two columns',
)

#----------------------------------------------------------------------
action_menu = html.Div(
		dcc.Dropdown(
			id = 'action-menu', 
			options=[
				{'label':'Add symbol', 'value':'Add symbol'},
				{'label':'Remove symbol', 'value':'Remove symbol'},
				{'label':'Add portfolio', 'value':'Add portfolio'},
				{'label':'Remove portfolio', 'value':'Remove portfolio'},
				{'label':'Update portfolio data', 'value':'Update portfolio'},
			], 
			value = '', 
			clearable=False,
			placeholder='Select an action'),
	className = 'two columns',
)

#----------------------------------------------------------------------
time_menu =	html.Div(
	dcc.Dropdown(id='time-menu', 
		options = [
			{'label':'1 Month','value':1},
			{'label':'2 Months','value':2},
			{'label':'3 Months','value':3},
			{'label':'6 Months','value':6},
			{'label':'1 Year','value':12},
			{'label':'2 Years','value':2*12},
			{'label':'3 Years','value':3*12},
			{'label':'4 Years','value':4*12},
			{'label':'5 Years','value':5*12},
		],
		clearable = False,
	), 
	className = 'two columns',
)

#----------------------------------------------------------------------
analysis_menu =html.Div(
	dcc.Dropdown(id='analysis-menu', 
		options = [
			{'label':'Forecast','value':'Forecast'},
			{'label':'Historical','value':'Historical'},
		],
		value = 'Forecast',
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

#----------------------------------------------------------------------
# Message for menu items.
#----------------------------------------------------------------------
# top_controls_message = html.Div(
# 	dcc.Loading(
# 		id='loading1',
# 		type='dot',
# 		fullscreen=True,
# 		children=[
# 			html.Div(
# 				id='portfolio-update-message', 
# 				style={'padding':'10px 0 0 10px'},
# 			),
# 		],
# 	),
# 	className='row', 
# 	style={
# 		'width':'95%', 
# 		'margin':'0 auto', 
# 		'color':'#bf2b21', 
# 		'border':'1px solid white',
# 		'height':'1px',
# 		# 'height':'55px',
# 		# 'display':'none',
# 	}
# )
