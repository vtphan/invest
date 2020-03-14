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
], style={'width':'90%'})

#---------------------------------------------------------------------------------------
app_layout = html.Div([	
	html.Div([
		# analysis_menu,
		# visualization_menu,
		portfolios_menu,
		action_menu,
		text_input,
		time_menu,
	], style={'width':'95%', 'margin':'0 auto', 'height':'55px'}),

	# top_controls_message,
	
	# Figures (top row)
	html.Div(
		dcc.Graph(id='figure1', config=dict(displayModeBar=False)), 
		style={'height':'350px', 'width':'35%', 'display':'inline-block', 'padding':'0', 'margin':'0'}),
	html.Div(
		dcc.Graph(id='figure2', config=dict(displayModeBar=False)), 
		style={'height':'350px', 'width':'35%', 'display':'inline-block', 'padding':'0', 'margin':'0'}),
	html.Div(
		dcc.Graph(id='figure3', config=dict(displayModeBar=False)), 
		style={'height':'350px', 'width':'30%', 'display':'inline-block', 'padding':'0', 'margin':'0'}),

	html.Div([
		html.Div(style={'margin-top':'1em', 'width':'100%'}),

		# Tables (bottom row)
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

