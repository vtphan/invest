from invest_layout_top import *
from invest_layout_middle import *
import dash_core_components as dcc 
import dash_html_components as html
from invest_time_range import time_range_layout

#---------------------------------------------------------------------------------------
hidden_divs = html.Div([
	dcc.Checklist(
		id='tickers', 
		options=[],
		value=[], 
		labelStyle={'display': 'none'}),
], className='row', style={'width':'90%'})

#---------------------------------------------------------------------------------------
app_layout = html.Div([	
	html.Div([
		analysis_menu,
		visualization_menu,
		time_menu,
		portfolios_menu,
		action_menu,
		text_input,
	], className='row', style={'width':'95%', 'margin':'0 auto', 'height':'55px'}),

	# top_controls_message,
	
	html.Div([
		html.Div([
			dcc.Graph(id='figure2'), 
			setup_table('table2'),
		], style={'width': '49%', 'display': 'inline-block', 'padding': '0'}),

		html.Div([
			dcc.Graph(id='figure1'), 
			setup_table('table1'),
		], style={'width': '49%', 'display': 'inline-block', 'padding': '0'}),

		time_range_layout(),
	], style={'width':'100%', 'margin':'0 auto'}),

	hidden_divs,
])

#---------------------------------------------------------------------------------------

