import plotly.express as px
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime as dt
import plotly.express as px
from dateutil import parser
import pytz

def is_datestring(string):
    try:
        parser.parse(string)
        return True
    except:
        return False

px.set_mapbox_access_token(open(".mapbox").read())

df = pd.read_parquet('/Users/bryanwang/Desktop/cashbnb/analysis/combined.parquet')

# limit to SF for now
df = df[df.publicAddress == 'San Francisco, CA, United States']

# fill NA for plotting reasons
df.fillna("NaN", inplace=True)

days = [c for c in df.columns if is_datestring(c)]

frames = [{
        # 'traces':[0],
        'name':'frame_{}'.format(day),
        'data':[{
            'type':'scattermapbox',
            'lat':df['lat'],
            'lon':df['long'],
            'marker':go.scattermapbox.Marker(
                color = df[day],
                showscale=True,
            ),
            # 'customdata':np.stack((df.xs(day)['confirmed_display'], df.xs(day)['recovered_display'],  df.xs(day)['deaths_display'], pd.Series(df.xs(day).index)), axis=-1),
            # 'hovertemplate': "<extra></extra><em>%{customdata[3]}  </em><br>🚨  %{customdata[0]}<br>🏡  %{customdata[1]}<br>⚰️  %{customdata[2]}",
        }],           
    } for day in days
]

data = frames[-1]['data']
active_frame = 0

sliders = [{
    'active':active_frame,
    'transition':{'duration': 0},
    'x':0.08,     #slider starting position  
    'len':0.88,
    'currentvalue':{
        'font':{'size':15}, 
        'prefix':'📅 ', # Day:
        'visible':True, 
        'xanchor':'center'
        },  
    'steps':[{
        'method':'animate',
        'args':[
            ['frame_{}'.format(day)],
            {
                'mode':'immediate',
                'frame':{'duration':250, 'redraw': True}, #100
                'transition':{'duration':100} #50
            }
            ],
        'label':day
    } for day in days]
}]

play_button = [{
    'type':'buttons',
    'showactive':True,
    'y':-0.08,
    'x':0.045,
    'buttons':[{
        'label':'🎬', # Play
        'method':'animate',
        'args':[
            None,
            {
                'frame':{'duration':250, 'redraw':True}, #100
                'transition':{'duration':100}, #50
                'fromcurrent':True,
                'mode':'immediate',
            }
        ]
    }]
}]

# fig = px.scatter_mapbox(df[df['publicAddress'] == 'San Francisco, CA, United States'], 
#     lat="lat", 
#     lon="long", 
#     color=days[0],
#     height=850)

layout = go.Layout(
    height=600,
    autosize=True,
    hovermode='closest',
    paper_bgcolor='rgba(0,0,0,0)',
    mapbox={
        'accesstoken':open(".mapbox").read(),
        # 'bearing':0,
        'center':{"lat": df['lat'].median(), "lon": df['long'].median()},
        # 'pitch':0,
        'zoom':10,
        'style':'dark',
    },
    updatemenus=play_button,
    sliders=sliders,
    margin={"r":0,"t":0,"l":0,"b":0}
)

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(figure=go.Figure(data=data, layout=layout, frames=frames), id='map'),
])


if __name__ == '__main__':
    app.run_server(debug=True)