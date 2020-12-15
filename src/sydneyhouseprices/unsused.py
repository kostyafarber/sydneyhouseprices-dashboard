# unused code that I may have to come back too

# geojson loading
geo_house_prices.to_file(os.path.join(cfg.files.json,"output.json"),driver="GeoJSON")

with open(os.path.join(cfg.files.json,"output.json")) as f:
          sydneygeojson = geojson.load(f)