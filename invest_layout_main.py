import dash_core_components as dcc 
import dash_html_components as html
from invest_time_range import time_range_layout
import dash_table

#---------------------------------------------------------------------------------------
def setup_table(table_id):
	return dash_table.DataTable(
		id=table_id,
		sort_action='native',
		# sort_action='custom',
		sort_mode='single',
		sort_by=[],
	    merge_duplicate_headers=True,
		style_header={
			'backgroundColor': '#cfcfcf',
			'fontWeight': 'bold',
		},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': '#e6e6e6',
			}
		],
		style_table={
			'maxHeight':'280px',
			'width':'90%',
			'margin':'0 auto',
			'overflowX':'scroll', 
			'overflowY':'scroll',
			'font-size':'120%',
		},
	)

#---------------------------------------------------------------------------------------
hidden_divs = html.Div([
	dcc.Checklist(
		id='tickers', 
		options=[],
		value=[], 
		labelStyle={'display': 'none'}),
], style={'width':'90%'})

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

#---------------------------------------------------------------------------------------

app_layout = html.Div([	
	html.Div([
		portfolios_menu,
		action_menu,
		text_input,
		time_menu,
	], style={'width':'95%', 'margin':'0 auto', 'height':'55px'}),

	# 3 figures (top row)
	html.Div(
		dcc.Graph(id='figure1', config=dict(displayModeBar=False)), 
		style={'height':'350px', 'width':'35%', 'display':'inline-block', 'padding':'0', 'margin':'0'}),
	html.Div(
		dcc.Graph(id='figure2', config=dict(displayModeBar=False)), 
		style={'height':'350px', 'width':'35%', 'display':'inline-block', 'padding':'0', 'margin':'0'}),
	html.Div(
		dcc.Graph(id='figure3', config=dict(displayModeBar=False)), 
		style={'height':'350px', 'width':'30%', 'display':'inline-block', 'padding':'0', 'margin':'0'}),

	# 2 tables (bottom row)
	html.Div([
		html.Div(style={'margin-top':'1em', 'width':'100%'}),

		html.Div(
			setup_table('table2'),
			style={'width':'49%', 'display':'inline-block', 'padding':'0', 'margin':0}),

		html.Div(
			setup_table('table1'),
			style={'width':'49%', 'display':'inline-block', 'padding':'0', 'margin':0}),

		# time_range_layout(),
	], style={'width':'100%', 'margin':'0 auto'}),

	hidden_divs,
])

#---------------------------------------------------------------------------------------

