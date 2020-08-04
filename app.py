# # -*- coding: utf-8 -*-

# # Run this app with `python app.py` and
# # visit http://127.0.0.1:8050/ in your web browser.

# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# import dash_table
# from datetime import datetime as dt
# from dateutil import parser
# import plotly.express as px
# import pandas as pd

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# # assume you have a "long-form" data frame
# # see https://plotly.com/python/px-arguments/ for more options

# # preprocessing
# samples = pd.read_csv("sample.csv", index_col='listingId')
# listings = pd.read_csv("data_listings.csv", index_col='_id')

# # this listings modification can be moved out
# listings.columns = [x.replace('data.listing.', '') for x in listings.columns]

# samples.columns = pd.to_datetime(samples.columns)

# # some code duplication to generate initial datatable
# # agg = samples.join(listings)
# # agg_null = (~samples.isnull()).join(listings)

# # booked = agg.groupby(['publicAddress', 'personCapacity'])[[c for c in agg.columns if isinstance(c, pd.Timestamp)]].sum().sum(axis=1)
# # total = agg_null.groupby(['publicAddress', 'personCapacity'])[[c for c in agg_null.columns if isinstance(c, pd.Timestamp)]].sum().sum(axis=1)

# # df = pd.concat([agg.groupby(['publicAddress', 'personCapacity']).size(),booked/total], axis=1)

# # samples = samples[[c for c in samples.columns if c > ds_to_utc(start_date) and c < ds_to_utc(end_date)]]

# app.layout = html.Div(children=[
#     dash_table.DataTable(
#         id='demand-table',
#         columns=[{"name": i, "id": i} for i in samples.columns],
#         # columns=[
#         #     {'name': i, 'id': i, 'deletable': True} for i in df.columns
#         #     # omit the id column
#         #     if i != 'id'
#         # ],
#         data=samples.to_dict('records'),
#     ),

#     dcc.DatePickerRange(
#         id='date-picker',
#         start_date=min([c for c in samples.columns if isinstance(c, pd.Timestamp)]),
#         end_date=max([c for c in samples.columns if isinstance(c, pd.Timestamp)]),
#     ),

#     dcc.RadioItems(
#     id='weekday-picker',
#     options=[
#         {'label': 'Sunday', 'value': 6},
#         {'label': 'Monday', 'value': 0},
#         {'label': 'Tuesday', 'value': 1},
#         {'label': 'Wednesday', 'value': 2},
#         {'label': 'Thursday', 'value': 3},
#         {'label': 'Friday', 'value': 4},
#         {'label': 'Saturday', 'value': 5},
#     ],
#     value=None,
#     labelStyle={'display': 'inline-block'}
# )  
# ])

# # janky global
# global_agg = None

# # @app.callback(
# #     dash.dependencies.Output('demand-table','data'),
# #     [dash.dependencies.Input('date-picker','start_date'),
# #      dash.dependencies.Input('date-picker','end_date'),
# #      dash.dependencies.Input('weekday-picker','value')])
# # def generate_datatable_from_filters(start_date, end_date, weekday):
# #     date_filter = lambda c: c > parser.parse(start_date) and c < parser.parse(end_date) and (weekday is None or c.weekday() == weekday)
# #     time_filtered = samples[[c for c in samples.columns if date_filter(c)]]

# #     # TODO: this condition needs to be changed / discussed
# #     time_filtered.dropna(how='all', inplace=True)

# #     agg = time_filtered.join(listings)

# #     # janky hack to keep track of state
# #     global_agg = agg
# #     agg_null = (~time_filtered.isnull()).join(listings)

# #     booked = agg.groupby(['publicAddress', 'personCapacity'])[[c for c in agg.columns if isinstance(c, pd.Timestamp)]].sum().sum(axis=1)
# #     total = agg_null.groupby(['publicAddress', 'personCapacity'])[[c for c in agg_null.columns if isinstance(c, pd.Timestamp)]].sum().sum(axis=1)

# #     return booked/total
#     # TODO: have a two tiered bar-chart, lower bar is number of booked houses, upper is total available for that day.
#     # TODO: have multiple metrics calculated, with option to sort by each.
#     # TODO: filter out places with less than n listings available in the given time period.











# if __name__ == '__main__':
#     app.run_server(debug=True)

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from datetime import datetime as dt
from dateutil import parser
import pytz

utc=pytz.UTC

samples = pd.read_csv("sample.csv", index_col='listingId')
listings = pd.read_csv("data_listings.csv", index_col='_id')

# this listings modification can be moved out
listings.columns = [x.replace('data.listing.', '') for x in listings.columns]

samples.columns = pd.to_datetime(samples.columns)

# convert bools to int for plotting
samples = samples*1


# TODO: pretty sure I can get rid of this part.
# some code duplication to generate initial datatable
agg = samples.join(listings)
agg_null = (~samples.isnull()).join(listings)

# possible error to report: plotly datatable cannot have integer column names
booked = agg.groupby(['publicAddress'])[[c for c in agg.columns if isinstance(c, pd.Timestamp)]].sum()
total = agg_null.groupby(['publicAddress'])[[c for c in agg_null.columns if isinstance(c, pd.Timestamp)]].sum().sum(axis=1)

df = (booked.sum(axis=1)/total).reset_index()
df.columns = ['publicAddress', 'demand']
print(df.head())

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        dcc.DatePickerRange(
            id='date-picker',
            start_date=min([c for c in samples.columns if isinstance(c, pd.Timestamp)]),
            end_date=max([c for c in samples.columns if isinstance(c, pd.Timestamp)]),
        ),

        dcc.RadioItems(
            id='weekday-picker',
            options=[
                {'label': 'Sunday', 'value': 6},
                {'label': 'Monday', 'value': 0},
                {'label': 'Tuesday', 'value': 1},
                {'label': 'Wednesday', 'value': 2},
                {'label': 'Thursday', 'value': 3},
                {'label': 'Friday', 'value': 4},
                {'label': 'Saturday', 'value': 5},
                {'label': 'All', 'value': -1}
            ],
            value=None,
            labelStyle={'display': 'inline-block'}
        ),

        dash_table.DataTable(
            id='demand-table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            page_size=10,
            row_selectable='single',
        )

    ],
    style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        html.Div(children='placeholder')
    ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'}, 
    id='conditional-graph')
])


# sometimes it's naive and sometimes it's timezone
def generate_utc_date(datestring):
    try:
        return utc.localize(parser.parse(datestring))
    except:
        return parser.parse(datestring)

@app.callback(
    dash.dependencies.Output('demand-table','data'),
    [dash.dependencies.Input('date-picker','start_date'),
     dash.dependencies.Input('date-picker','end_date'),
     dash.dependencies.Input('weekday-picker','value')])
def generate_datatable_from_filters(start_date, end_date, weekday):
    date_filter = lambda c: c > generate_utc_date(start_date) and c < generate_utc_date(end_date) and (weekday is None or weekday == -1 or c.weekday() == weekday)
    time_filtered = samples[[c for c in samples.columns if date_filter(c)]]

    # TODO: this condition needs to be changed / discussed
    time_filtered.dropna(how='all', inplace=True)

    agg = time_filtered.join(listings)

    agg_null = (~time_filtered.isnull()).join(listings)


    # janky hack, needs to be changed if more people use this.
    global booked
    booked = agg.groupby(['publicAddress'])[[c for c in agg.columns if isinstance(c, pd.Timestamp)]].sum()
    total = agg_null.groupby(['publicAddress'])[[c for c in agg_null.columns if isinstance(c, pd.Timestamp)]].sum().sum(axis=1)

    new_df = (booked.sum(axis=1)/total).reset_index()
    new_df.columns = ['publicAddress', 'demand']
    # print("-------", new_df)
    return new_df.to_dict('records')


@app.callback(
    dash.dependencies.Output('conditional-graph','children'),
    [dash.dependencies.Input('date-picker','start_date'),
     dash.dependencies.Input('date-picker','end_date'),
     dash.dependencies.Input('weekday-picker','value'),
     dash.dependencies.Input('demand-table', "derived_virtual_selected_rows")])
def generate_conditional_graphs(start_date, end_date, weekday, derived_virtual_selected_rows):
    if derived_virtual_selected_rows is None or derived_virtual_selected_rows == []:
        return

    # print("derived virtual selected",derived_virtual_selected_rows)
    global booked

    # TODO: this might need to be changed if the original df gets permuted.
    address = booked.iloc[derived_virtual_selected_rows[0]] # only one can be selected.

    print(address)

    return [dcc.Graph(
        id=f"conditional-graph-{derived_virtual_selected_rows[0]}",
        figure={
            "data": [
                {
                    "x": booked.columns,
                    "y": address.values,
                    "type": "bar",
                }
            ],
            "layout": {
                "xaxis": {"automargin": True},
                "yaxis": {"automargin": True},
                "height": 250,
                "margin": {"t": 100, "l": 10, "r": 10},
                "title": f"Demand Over Time for {booked.index[derived_virtual_selected_rows[0]]}"
            },
        },
    )]
    
    


if __name__ == '__main__':
    app.run_server(debug=True)