import dash_core_components as dcc 
import dash_html_components as html
import numpy as np
import datetime


#---------------------------------------------------------------------------------------
def time_range_layout(): 
	return html.Div(html.Div(
		# dcc.RangeSlider(
		dcc.RangeSlider(
			id='time-range', 
			step=1, 
			max=0,
			pushable=1,
			allowCross=False,
		),
		style = {'padding':'2em', 'margin':'0'},
		className = 'twelves columns',
	), className = 'row', style = {'width':'90%', 'margin':'0 auto'})

#------------------------------------------------------------------------------
def time_range_callback(months_ago):
	min_weeks = -months_ago*4
	left = -months_ago*2
	inc = np.round(min_weeks/10,0)
	marks = np.array(range(10)) * inc 
	if min_weeks == -240:
		marks = [0, -24, -48, -72, -96, -120, -144, -168, -192, -216, -240]
	elif min_weeks == -192:
		marks = [0, -19,  -38,  -57,  -76,  -95, -114, -133, -152, -171, -190]
	elif min_weeks == -144:
		marks = [0,  -14,  -28,  -42,  -56,  -70,  -84,  -98, -112, -126, -140]
	elif min_weeks == -96:
		marks = [0, -10, -20, -30, -40, -50, -60, -70, -80, -90]
	elif min_weeks == -48:
		marks = [0, -5, -10, -15, -20, -25, -30, -35, -40, -45]
	elif min_weeks == -24:
		marks = [0, -3, -6, -9, -12, -15, -18, -21, -24]
	elif min_weeks == -12:
		marks = [0, -2, -4, -6, -8, -10, -12]
	elif min_weeks == -8:
		marks = [0, -2, -4, -6, -8]
	elif min_weeks == -4:
		marks = [0, -1, -2, -3, -4]
	today = datetime.datetime.today()
	marks_labels = {}
	for m in marks:
		date = today - datetime.timedelta(days=-m*7)
		marks_labels[int(m)] = date.strftime('%Y-%b-%d')
	return min_weeks, [left,0], marks_labels

#------------------------------------------------------------------------------
	