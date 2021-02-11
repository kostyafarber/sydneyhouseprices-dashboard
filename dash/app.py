import pandas as pd
import geopandas as gpd

import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import dash
import dash_core_components as dcc
import dash_html_components as html

from sydneyhouseprices.data import remoteGeoJSONToGDF

# Preparing Data

# import dataframe
df = pd.read_csv('prices_data.csv', parse_dates=True, index_col='Date')

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
data = px.choropleth_mapbox(geo_house_prices,
                            geojson=geo_house_prices.geometry,
                            locations=geo_house_prices.index, color='sellPrice',
                            color_continuous_scale="viridis",
                            center={"lat": -33.865143, "lon": 151.209900},
                            range_color=(0, 2000000),
                            labels={"sellPrice": "Selling Price", "suburb": "Suburb"},
                            mapbox_style='open-street-map',
                            opacity=0.5
                            )

fig = go.Figure(data=data)

fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
fig.update_geos(fitbounds="locations", visible=False)

app = dash.Dash(external_stylesheets=dbc.themes.JOURNAL)
app.run_server(debug=True)
