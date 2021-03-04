<img src='/plotly_dashboard/assets/puzzle.png' align='right'>

## Sydney House Prices Dashboard | Exploratory Analysis Notebook

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/kostyafarber/sydneyhouseprices-dashboard/HEAD?filepath=%2Fjupyter_notebook%2Fsydney_choropleth.ipynb)
[![Heroku](https://heroku-badge.herokuapp.com/?app=heroku-badge)](https://sydneyhouseprices-dashboard.herokuapp.com/)



![](/plotly_dashboard/assets/dash.png)

## Installation
The deployed dashboard is available to view by clicking on the badge icon above.

To run the dashboard locally clone the repository and `cd` into it:

```shell
$ git clone https://github.com/kostyafarber/sydneyhouseprices-dashboard.git
```

and change into the `plotly_dashboard` directory:

```shell
$ cd plotly_dashboard/      
```

Create a Python virtual environment, activate it and install the required dependencies in `requirements.txt`:

```shell
$ virtualenv dashboard
$ source dashboard/bin/activate # Windows: \venv\scripts\activate
$ pip install -r requirements.txt
```

*Optional*: 
You will need a mapbox token to reproduce the exact same style for the map, so you can create a [mapbox](https://www.mapbox.com/) account and copy and paste your API code into a file called
`.mapbox_token` into the root directory.

Then run `app.py` and it will serve the app locally:

```shell
$ python app.py
```
## Data
The data was obtained on [Kaggle](https://www.kaggle.com/mihirhalai/sydney-house-prices/activity). An in-depth Jupyter notebook is available that explores the data and contains the code that produced the plots in the dashboard in the `jupyter_notebook` directory. To view an executable version of the notebook click on the binder badge in the title. 

Otherwise you may use the `environment.yml` in `binder` to create your own conda environment and run it locally with the required dependencies.
