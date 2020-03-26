import dash_core_components as dcc 
import dash_html_components as html
from invest_time_range import time_range_layout
import dash_table
from invest_utils import index_list
import datetime

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
			'width':'97%',
			'margin':'0 auto',
			'overflowX':'scroll', 
			'overflowY':'scroll',
			'font-size':'120%',
		},
	)

#---------------------------------------------------------------------------------------
hidden_divs = html.Div(dcc.Checklist(id='tickers',options=[],value=[],labelStyle={'display':'none'}))

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
index_menu = html.Div(
	dcc.Dropdown(
		id = 'index-menu', 
		options = index_list(),
		value = '',
		clearable = True,
		placeholder='INDEX',
	),
	className = 'two columns',
)

#----------------------------------------------------------------------
action_menu = html.Div(
		dcc.Dropdown(
			id = 'action-menu', 
			options=[
				{'label':'Add symbol', 'value':'Add symbol'},
				{'label':'Save symbol', 'value':'Save symbol'},
				{'label':'Remove symbol', 'value':'Remove symbol'},
				{'label':'Add index', 'value':'Add index'},
				{'label':'Remove index', 'value':'Remove index'},
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
time_slider = html.Div(
	dcc.Slider(
		id = 'time-slider',
		min = 1,
		max = 52,
		# step = 1,
		marks = { i:''.format(i) for i in [1,2,3,4,6,8,10,12,16,20,24] },
		# marks = { i : '{}w'.format(i) for i in range(1,53) },
		value = 1,
	),
	className = 'four columns',
)

#----------------------------------------------------------------------
time_menu =	html.Div(
	dcc.RadioItems(id='time-menu', 
		options = [
			{'label':'1W','value':'1W'},
			{'label':'2W','value':'2W'},
			{'label':'3W','value':'3W'},
			{'label':'1M','value':'1M'},
			{'label':'1.5M','value':'1.5M'},
			{'label':'2M','value':'2M'},
			{'label':'3M','value':'3M'},
			{'label':'4M','value':'4M'},
			{'label':'6M','value':'6M'},
			{'label':'9M','value':'9M'},
			{'label':'1Y','value':'1Y'},
			{'label':'1.5Y','value':'1.5Y'},
			{'label':'2Y','value':'2Y'},
		],
		value='2W',
        labelStyle={'display': 'inline-block'},
	), 
	className = 'four columns',
)

#----------------------------------------------------------------------
date_picker = html.Div(
    dcc.DatePickerSingle(
        id='date-picker',
        min_date_allowed=datetime.date.today() - datetime.timedelta(days=365*3),
        max_date_allowed=datetime.date.today() - datetime.timedelta(days=1),
        date=datetime.date.today() - datetime.timedelta(days=14),
        # initial_visible_month=dt(2017, 8, 5),
    ),
	className = 'four columns',
)
#---------------------------------------------------------------------------------------

app_layout = html.Div([	
	html.Div([
		portfolios_menu,
		index_menu,
		action_menu,
		text_input,
		date_picker,
		# time_menu,
	], style={'width':'95%', 'margin':'0 auto', 'height':'55px'}),

	# 3 figures (top row)
	html.Div(
		dcc.Graph(id='figure1', config=dict(displayModeBar=False)), 
		style={'height':'405px', 'width':'36%', 'display':'inline-block', 'padding':'0', 'margin':'0'}),
	html.Div(
		dcc.Graph(id='figure2', config=dict(displayModeBar=False)), 
		style={'height':'405px', 'width':'36%', 'display':'inline-block', 'padding':'0', 'margin':'0'}),
	html.Div(
		dcc.Graph(id='figure3', config=dict(displayModeBar=False)), 
		style={'height':'405px', 'width':'27%', 'display':'inline-block', 'padding':'0', 'margin':'0'}),

	# 2 tables (bottom row)
	html.Div([
		html.Div(style={'margin-top':'1em', 'width':'100%'}),

		html.Div(
			setup_table('secondary-table'),
			style={'width':'44%', 'display':'inline-block', 'padding':'0', 'margin':0}),

		html.Div(
			setup_table('main-table'),
			style={'width':'55%', 'display':'inline-block', 'padding':'0', 'margin':0}),

		# time_range_layout(),
	], style={'width':'100%', 'margin':'0 auto'}),

	hidden_divs,
])

#---------------------------------------------------------------------------------------

