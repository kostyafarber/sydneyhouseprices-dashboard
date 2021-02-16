import pandas as pd
import geopandas as gpd
import os
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import dash
import dash_core_components as dcc
import dash_html_components as html
import os
from sydneyhouseprices.data import remoteGeoJSONToGDF

# Preparing Data

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

# choropleth map
# ---------------------------------------------------------------------------------------------------------------------
token = open('.mapbox_token').read()

fig = px.choropleth_mapbox(geo_house_prices,
                            geojson=geo_house_prices.geometry,
                            locations=geo_house_prices.index, color='sellPrice',
                            color_continuous_scale="viridis",
                            center={"lat": -33.865143, "lon": 151.209900},
                            range_color=(0, 2000000),
                            labels={"sellPrice": "Selling Price", "suburb": "Suburb"},
                            opacity=0.3
                            )

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                  mapbox_style="dark",
                  mapbox_accesstoken=token,
                  template='plotly_dark'
                  )
fig.update_coloraxes(colorbar_title=dict(side='right'))
fig.update_geos(fitbounds="locations", visible=False)

# ---------------------------------------------------------------------------------------------------------------------
# Count Number of sales made in each month and turn into a dataframe
sold_per_month = pd.DataFrame(df.index.month_name().value_counts())

# Rename Date column to Sold per Month
sold_per_month.rename(columns={'Date':'Sold per Month'},inplace=True)
sold_per_month.head()


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

server = app.server

# Layouts
# ---------------------------------------------------------------------------------------------------------------------
app.layout = dbc.Container([

    dbc.Row([
        dbc.Col(html.H4("Sydney House Prices"),
                className='text-left')
    ],className='m-3'),

    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig))
    ], className='m-3')
],fluid=True)

if __name__ == '__main__':
    app.run_server(debug=True)
