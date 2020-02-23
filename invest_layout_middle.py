import dash_core_components as dcc 
import dash_html_components as html 
import dash_table

#---------------------------------------------------------------------------------------
def setup_table(table_id):
	return dash_table.DataTable(
		id=table_id,
		sort_action='custom',
		sort_mode='single',
		sort_by=[],
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
			'maxHeight':'200px',
			'width':'90%',
			'margin':'0 auto',
			'overflowX':'scroll', 
			'overflowY':'scroll',
			'font-size':'120%',
		},
	)


