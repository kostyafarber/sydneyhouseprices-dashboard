import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import geopandas as gpd
import pandas as pd
import plotly.express as px
import requests
from dash.dependencies import Input, Output
import os

# check for tokens
token = os.getenv('MAPBOX_TOKEN')
mapbox_style = "dark"
if not token:
    try:
        token = open('.mapbox_token').read()
    except Exception as e:
        print('mapbox token not found, using open-street-maps')
        mapbox_style = "carto-darkmatter"

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


# function to plot histograms
def plot_hist(x, df, new_label, range_list, title):
    """

    :param x: x column of dataframe
    :param df: dataframe
    :param new_label: new label to replace existing one
    :param range_list: a range of x limits in list format
    :param title: plot title
    :return: returns figure
    """
    figure = px.histogram(data_frame=df, x=x, template='plotly_dark', labels={x: new_label}, height=300)

    figure.update_layout(
        dict(title=title, plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)'),
        yaxis=dict(showgrid=False),
        xaxis=dict(showgrid=False))
    figure.update_xaxes(range=range_list)
    figure.update_traces(marker=dict(color=px.colors.sequential.Viridis[-4]))

    return figure


stat_labels = ['Selling Price is {:.2f}', 'Number of Bedrooms is {:.2f}', 'Number of Bathrooms is {:.2f}',
               'Number of Carspaces is {:.2f}']

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
fig = px.choropleth_mapbox(geo_house_prices,
                           geojson=geo_house_prices.geometry,
                           locations=geo_house_prices.index, color='sellPrice',
                           color_continuous_scale="viridis",
                           center={"lat": -33.865143, "lon": 151.209900},
                           range_color=(0, 2000000),
                           labels={"sellPrice": "Selling Price", "suburb": "Suburb"},
                           opacity=0.6,
                           zoom=10
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
                     colorbar=dict(x=0.92, xpad=0))
fig.update_geos(fitbounds="locations", visible=False)

# Histograms
# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
# Count Number of sales made in each month and turn into a dataframe
sold_per_month = pd.DataFrame(df.index.month_name().value_counts())

# Rename Date column to Sold per Month
sold_per_month.rename(columns={'Date': 'Sold per Month'}, inplace=True)
sold_per_month.head()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

# Layouts
# ---------------------------------------------------------------------------------------------------------------------
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H5(["Sydney Housing Market Dashboard",

                     html.A(
                         html.Img(
                             src='assets/puzzle.png',
                             style={'float': 'right', 'height': '28px',
                                    'margin-right': '1%', 'margin-top': '-7px'}
                         ),
                     href='https://kostyafarber.github.io/'),

                     html.Img(
                         src='assets/dash-logo.png',
                         style={'float': 'right', 'height': '28px',
                                'margin-right': '1%', 'margin-top': '-7px'}
                     )
                     ])
        ])
    ]),

    dbc.Row([
        dbc.Col(html.H5(id='price'), className='pretty_container text-center'),
        dbc.Col(html.H5(id='bedrooms'), className='pretty_container text-center'),
        dbc.Col(html.H5(id='bathrooms'), className='pretty_container text-center'),
        dbc.Col(html.H5(id='carspace'), className='pretty_container text-center')
    ]),

    dbc.Row([
        dbc.Col([
            html.H6(id='header', className='container_title'),
            dcc.Graph(figure=fig, id='map'),
        ], className='pretty_container twelve columns')
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='bed'), className='pretty_container six columns'),

        dbc.Col(dcc.Graph(id='sell'), className='pretty_container six columns'),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='car'), className='pretty_container six columns'),

        dbc.Col(dcc.Graph(id='bath'), className='pretty_container six columns')
    ]),

    dbc.Row([
            dbc.Col([
                html.H5('Additional Information', className='container_title'),
                dcc.Markdown('''
                * Data was obtained from Kaggle [here](https://www.kaggle.com/mihirhalai/sydney-house-prices/activity). Data was scraped from realestate.com from 2010-2019.
                * For more in-depth analysis see my [Jupyter Notebook](https://nbviewer.jupyter.org/github/kostyafarber/sydneyhouseprices/blob/master/notebooks/sydney_choropleth.ipynb) and the source code on [GitHub](https://github.com/kostyafarber/sydneyhouseprices).
                * Thank you rapidsai for the great CSS and inspiration for the layout of this dashboard. Check out their GitHub Repo [here](https://github.com/rapidsai/plotly-dash-rapids-census-demo)
                * Check out the source code for this project on [Github](https://github.com/kostyafarber/sydneyhouseprices-dashboard)
                * For more about me, visit my blog by clicking on the jigsaw icon in the top right corner of this dashboard!
                ''')
                ])
    ], className='pretty_container')

], fluid=True)



@app.callback(
    Output('header', 'children'),
    Input('map', 'clickData')
)
def update_header(clickData):
    if clickData is None:
        return 'Median House Prices Sydney'
    else:
        location = clickData['points'][0]['location']

        return 'Median House Prices Sydney (suburb selected {})'.format(location)


@app.callback([
    Output('price', 'children'),
    Output('bedrooms', 'children'),
    Output('bathrooms', 'children'),
    Output('carspace', 'children')],
    [Input('map', 'clickData')]
)
def update_info(clickData):
    if clickData is None:
        sydney_stats = median_statistics.median().values

        output = []

        for label, stat in zip(stat_labels, sydney_stats):
            output.append(label.format(stat))

        return output
    else:

        location = clickData['points'][0]['location']
        stats_location = median_statistics[median_statistics.index == location].median().values

        output = []

        for label, stat in zip(stat_labels, stats_location):
            output.append(label.format(stat))

        return output


@app.callback(
    Output('bed', 'figure'),
    Input('map', 'clickData'))
def update_histogram(clickData):
    if clickData is None:
        bed = plot_hist('bed', df, 'Number of Beds', [0, 10], 'Number of Beds Histogram')

        return bed

    else:
        location = clickData['points'][0]['location']
        dff = df[df['suburb'] == location]
        bed = plot_hist('bed', dff, 'Number of Beds', [0, 10], 'Number of Beds Histogram in {0}'.format(location))

        return bed


@app.callback(
    Output('bath', 'figure'),
    Input('map', 'clickData'))
def update_histogram(clickData):
    if clickData is None:
        bath = plot_hist('bath', df, 'Number of Baths', [0, 10], 'Number of Baths Histogram')

        return bath

    else:

        location = clickData['points'][0]['location']
        dff = df[df['suburb'] == clickData['points'][0]['location']]

        bath = plot_hist('bath', dff, 'Number of Baths', [0, 10],
                         'Number of Bathrooms Histogram in {0}'.format(location))

        return bath


@app.callback(
    Output('car', 'figure'),
    Input('map', 'clickData'))
def update_histogram(clickData):
    if clickData is None:
        car = plot_hist('car', df, 'Number of Cars', [0, 10], 'Number of Cars Histogram')

        return car

    else:

        location = clickData['points'][0]['location']
        dff = df[df['suburb'] == clickData['points'][0]['location']]

        car = plot_hist('car', dff, 'Number of Cars', [0, 10], 'Number of Cars Histogram in {0}'.format(location))

        return car


@app.callback(
    Output('sell', 'figure'),
    Input('map', 'clickData'))
def update_histogram(clickData):
    if clickData is None:
        sell = plot_hist('sellPrice', df, 'Selling Price in Millions (AUD)', [0, 2500000], 'Number of Baths Histogram')

        return sell

    else:
        location = clickData['points'][0]['location']
        dff = df[df['suburb'] == clickData['points'][0]['location']]

        sell = plot_hist('sellPrice', dff, 'Selling Price in Millions (AUD)', [0, 2500000],
                         'Selling Property Price Histogram '
                         'in {0}'.format(location))
        return sell


if __name__ == '__main__':
    app.run_server(debug=True)
