import requests
import geopandas as gpd


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

