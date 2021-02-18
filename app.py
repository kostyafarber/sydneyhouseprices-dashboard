import pandas as pd
import geopandas as gpd
import plotly.express as px
import dash_bootstrap_components as dbc
import dash
import dash_core_components as dcc
import dash_html_components as html
import requests


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
                           opacity=0.3,
                           height=1000
                           )

fig.update_layout(mapbox_style="dark",
                  mapbox_accesstoken=token,
                  template='plotly_dark',
                  paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)',
                  title='Median Sydney House Prices',
                  margin={'r': 0, 'l': 0},
                  autosize=True
                  )
fig.update_coloraxes(colorbar_title=dict(side='right', text='Selling Price in Millions (AUD)'))
fig.update_geos(fitbounds="locations", visible=False)

# Histograms
# ---------------------------------------------------------------------------------------------------------------------
bed = px.histogram(data_frame=df, x='bed', template='plotly_dark', color_discrete_sequence=px.colors.sequential.Viridis[-1],
                   labels={'bed': 'Number of Bedrooms'}, height=300)
bed.update_layout(dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', title='Bedrooms Histogram'))
bed.update_xaxes(range=[0, 10])

bath = px.histogram(data_frame=df, x='bath', template='plotly_dark',
                    color_discrete_sequence=px.colors.sequential.Viridis[-1], labels={'bath': 'Number of Bathrooms'},
                    height=300)
bath.update_layout(dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', title='Bathrooms Histogram'))
bath.update_xaxes(range=[0, 10])

car = px.histogram(data_frame=df, x='car', template='plotly_dark', color_discrete_sequence=px.colors.sequential.Viridis[-1],
                   labels={'car': 'Number of Car Spaces'}, height=300)
car.update_layout(dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', title='Car Spaces Histogram'))
car.update_xaxes(range=[0, 10])

sell = px.histogram(data_frame=df, x='sellPrice', template='plotly_dark',
                    color_discrete_sequence=px.colors.sequential.Viridis[-1],
                    labels={'sellPrice': 'Selling Price in Millions (AUD)'}, height=300)
sell.update_layout(dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', title='Selling Prices Histogram'))
sell.update_xaxes(range=[0, 10000000])

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
        dbc.Col(dcc.Graph(figure=fig)),

        dbc.Col(children=[
            dbc.Row([

                dbc.Alert(
                    (
                        html.H1('Sydney House Prices'),

                        html.Hr(className='my-2', style={'borderColor': 'white'}, ),

                        html.P(
                            "Welcome to my dashboard. Sydney Property Prices are always a focal attention in Australian News. "
                            "Here you have various "
                            "graphs that can help you better understand the Sydney property market."
                        ),
                    )
                ),
            ]),

            dbc.Row([

                dbc.Col(dcc.Graph(figure=bed)),

                dbc.Col(dcc.Graph(figure=car))

            ]),

            dbc.Row([

                dbc.Col(dcc.Graph(figure=bath)),

                dbc.Col(dcc.Graph(figure=sell))

            ])
        ]
        ),
    ], no_gutters=False),

], fluid=True)

if __name__ == '__main__':
    app.run_server(debug=True)
