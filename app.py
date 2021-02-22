import pandas as pd
import geopandas as gpd
import plotly.express as px
import dash_bootstrap_components as dbc
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import requests
import json


# Function to import geojson and change to geopandas dataframe
def remoteGeoJSONToGDF(url, display=False):
    """Import remote GeoJSON to a GeoDataFrame
    Keyword arguments:
    url -- URL to GeoJSON resource on web
    display -- Displays geometries upon loading (default: False)
    """
    r = requests.get(url)
    data = r.json()
    gdf = gpd.GeoDataFrame.from_features(data['features'])
    if display:
        gdf.plot()
    return gdf


# Preparing Data
# ---------------------------------------------------------------------------------------------------------------------
# import dataframe
df = pd.read_csv('data/prices_data.csv', parse_dates=True, index_col='Date')

sydney = remoteGeoJSONToGDF('https://raw.githubusercontent.com/Perishleaf/data-visualisation-scripts/master'
                            '/dash_project_medium/Sydney_suburb.geojson')

# cleaning the geopandas dataframe
sydney = sydney[["geometry", "nsw_loca_2"]]
sydney.rename(columns={"nsw_loca_2": "suburb"}, inplace=True)

# change to proper nouns to match our geojson file
sydney.suburb = sydney.suburb.str.title()

# Median Stats
median_statistics = df.groupby("suburb").median()

# Create merged geopandas df
geo_house_prices = pd.merge(sydney, median_statistics, left_on="suburb", right_on=median_statistics.index, how="inner")
geo_house_prices.set_index("suburb", inplace=True)

# Choropleth Map
# ---------------------------------------------------------------------------------------------------------------------
token = open('.mapbox_token').read()

fig = px.choropleth_mapbox(geo_house_prices,
                           geojson=geo_house_prices.geometry,
                           locations=geo_house_prices.index, color='sellPrice',
                           color_continuous_scale="viridis",
                           center={"lat": -33.865143, "lon": 151.209900},
                           range_color=(0, 2000000),
                           labels={"sellPrice": "Selling Price", "suburb": "Suburb"},
                           opacity=0.6,
                           height=800,
                           zoom=8.5
                           )

fig.update_layout(mapbox_style="dark",
                  template='plotly_dark',
                  mapbox_accesstoken=token,
                  autosize=True,
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  margin=dict(l=0, r=0, t=0, b=0)
                  )
fig.update_coloraxes(colorbar_title=dict(side='right', text='Selling Price in Millions (AUD)'),
                     colorbar=dict(x=0.90, xpad=0))
fig.update_geos(fitbounds="locations", visible=False)

# Histograms
# ---------------------------------------------------------------------------------------------------------------------
bed = px.histogram(data_frame=df, x='bed', template='plotly_dark',
                   labels={'bed': 'Number of Bedrooms'}, height=300)
bed.update_layout(dict(title='Bedrooms Histogram', plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)'))
bed.update_xaxes(range=[0, 10])
bed.update_traces(marker=dict(color=px.colors.sequential.Viridis[-4]))

bath = px.histogram(data_frame=df, x='bath', template='plotly_dark',
                    labels={'bath': 'Number of Bathrooms'},
                    height=300)
bath.update_layout(dict(title='Bathrooms Histogram', plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)'))
bath.update_xaxes(range=[0, 10])
bath.update_traces(marker=dict(color=px.colors.sequential.Viridis[-4]))

car = px.histogram(data_frame=df, x='car', template='plotly_dark',
                   labels={'car': 'Number of Car Spaces'}, height=300)
car.update_layout(dict(title='Car Histogram', plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)'))
car.update_xaxes(range=[0, 10])
car.update_traces(marker=dict(color=px.colors.sequential.Viridis[-4]))

sell = px.histogram(data_frame=df, x='sellPrice', template='plotly_dark',
                    labels={'sellPrice': 'Selling Price in Millions (AUD)'}, height=300)
sell.update_layout(
    dict(title='Selling Prices Histogram', plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)'))
sell.update_xaxes(range=[0, 10000000])
sell.update_traces(marker=dict(color=px.colors.sequential.Viridis[-4]))
# ---------------------------------------------------------------------------------------------------------------------
# Count Number of sales made in each month and turn into a dataframe
sold_per_month = pd.DataFrame(df.index.month_name().value_counts())

# Rename Date column to Sold per Month
sold_per_month.rename(columns={'Date': 'Sold per Month'}, inplace=True)
sold_per_month.head()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

server = app.server

# Layouts
# ---------------------------------------------------------------------------------------------------------------------
app.layout = dbc.Container([

    dbc.Row([
        dbc.Col(children=[
            html.H4("The Sydney Housing Market from 2000-2019", className='font-weight-light'),
            html.H5("Explore the median selling prices for Sydney properties and their attributes",
                    className='font-weight-light')
        ]),

        dbc.Col(children=[
            html.Img(src='assets/puzzle.png', width=30, height=30, className='m-1 img-fluid'),
            html.Img(src='assets/plotly_dash.png', width=128, height=128, className='m-1 img-fluid'),
        ], style={'textAlign': 'right'})
    ]),

    dbc.Row([
        dbc.Col(
            dcc.Graph(figure=fig, id='map', className='bg-dark m-1')
        ),

        dbc.Col(children=[

            dbc.Row([

                dbc.Col(dcc.Graph(figure=bed), className='m-1 bg-dark'),

                dbc.Col(dcc.Graph(figure=car), className='m-1 bg-dark')

            ]),

            dbc.Row([

                dbc.Col(dcc.Graph(figure=bath), className='m-1 bg-dark'),

                dbc.Col(dcc.Graph(figure=sell), className='m-1 bg-dark'),
            ]),

            dbc.Row([
                dbc.Col(html.Pre(id='click-data'), className='m-1 bg-dark')
            ])
        ]),
    ]),

], fluid=True)


@app.callback(
    Output('click-data', 'children'),
    Input('map', 'clickData'))
def display_hover_data(clickData):
    return json.dumps(clickData, indent=2)


if __name__ == '__main__':
    app.run_server(debug=True)
