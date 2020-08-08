import plotly.express as px
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime as dt
import plotly.express as px
from graph_utils import create_map_scatter
from helper_utils import *

px.set_mapbox_access_token(open(".mapbox").read())

df = pd.read_parquet('/Users/bryanwang/Desktop/cashbnb/analysis/combined_nongraph.parquet')
pa = pd.read_csv('/Users/bryanwang/Desktop/cashbnb/analysis/publicAddress.csv')

days = [c for c in df.columns if is_datestring(c)]

print("finished reading files")

app = dash.Dash(__name__)

@app.callback(
    dash.dependencies.Output('map','figure'),
    [dash.dependencies.Input('demand-table', "derived_virtual_selected_rows"), 
    dash.dependencies.Input('personCapacity-dropdown', "value"),
    dash.dependencies.Input('minNights-dropdown', "value"),
    dash.dependencies.Input('reviewsCount-dropdown', "value")])
def update_map(derived_virtual_selected_rows, personCapacity, minNights, reviewsCount):
    if derived_virtual_selected_rows is None or derived_virtual_selected_rows == []:
        address = 'San Francisco, CA, United States'
    else:
        address = pa.iloc[derived_virtual_selected_rows[0]].publicAddress

    print(f"i'm in the callback with address: {address}")

    sub_df = df[df.publicAddress == address]

    if isinstance(personCapacity, int):
        sub_df = sub_df[sub_df.personCapacity == personCapacity]

    if isinstance(minNights, int):
        sub_df = sub_df[sub_df.minNights == minNights]

    if isinstance(reviewsCount, int):
        sub_df = sub_df[sub_df.reviewsCount >= reviewsCount]

    return create_map_scatter(sub_df)



app.layout = html.Div([
    html.Div([
        dcc.Graph(figure=create_map_scatter(df[df.publicAddress == 'San Francisco, CA, United States']), 
        id='map')
    ],style={'width': '70%', 'display': 'inline-block'}),
    html.Div([
        html.H2(children='Location'),
        dash_table.DataTable(
            id='demand-table',
            columns=[{"name": i, "id": i} for i in pa.columns],
            data=pa.to_dict('records'),
            page_size=10,
            row_selectable='single',
        ),
        html.H2(children='Person Capacity'),
        dcc.Dropdown(
        id='personCapacity-dropdown',
        options=[
            {'label': '2', 'value': 2},
            {'label': '3', 'value': 3},
            {'label': '4', 'value': 4},
            {'label': '6', 'value': 6},
            {'label': 'all', 'value': 'all'},
        ],
        value='all'
        ),
        html.H2(children='Minimum Nights'),
        dcc.Dropdown(
        id='minNights-dropdown',
        options=[
            {'label': '1', 'value': 1},
            {'label': '2', 'value': 2},
            {'label': '3', 'value': 3},
            {'label': '4', 'value': 4},
            {'label': '30', 'value': 30},
            {'label': 'all', 'value': 'all'},
        ],
        value='all'
        ),
        html.H2(children='Reviews Count'),
        dcc.Dropdown(
        id='reviewsCount-dropdown',
        options=[
            {'label': '>= 10', 'value': 10},
            {'label': '>= 20', 'value': 20},
            {'label': '>= 30', 'value': 30},
            {'label': 'all', 'value': 'all'},
        ],
        value='all'
        )
    ],style={'width': '28%', 'float': 'right', 'display': 'inline-block'}, 
    id='conditional-graph')
])


if __name__ == '__main__':
    app.run_server(debug=True)