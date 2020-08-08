import plotly.express as px
from helper_utils import *
import pandas as pd

def create_map_scatter(df, zoom=11):
    # fill NaNs for the plot to work
    df.fillna("unavailable", inplace=True)
    df = pd.melt(df, id_vars=['index', 'publicAddress', 'lat', 'long', 'name', 'reviewsCount', 'personCapacity', 'minNights'], 
    value_vars=[c for c in df.columns if is_datestring(c)])
    
    return px.scatter_mapbox(df, 
        lat="lat", 
        lon="long", 
        color='value',
        height=850,
        animation_frame='variable',
        animation_group='index',
        hover_data=['name', 'reviewsCount', 'personCapacity', 'minNights'],
        zoom=zoom)

def create_map(derived_virtual_selected_rows):
    if derived_virtual_selected_rows is None or derived_virtual_selected_rows == []:
        print("i'm in callback with null")
        address = "San Francisco, CA, United States"
    else:
        address = pa.iloc[derived_virtual_selected_rows[0]].publicAddress

    sub_df = df[df.publicAddress == address].head()

    start_date = '2020-08-07'
    end_date = '2020-08-30'

    days = [c for c in df.columns if is_datestring(c) and c > generate_utc_date(start_date) and c < generate_utc_date(end_date)]

    frames = [{
            # 'traces':[0],
            'name':'frame_{}'.format(day),
            'data':[{
                'type':'scattermapbox',
                'lat':sub_df['lat'],
                'lon':sub_df['long'],
                'marker':go.scattermapbox.Marker(
                    color = sub_df[day],
                    showscale=True,
                    opacity=0.5,
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

    layout = go.Layout(
        height=800,
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

    print("returning figure")
    return go.Figure(data=data, layout=layout, frames=frames)