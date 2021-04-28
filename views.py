from flask import Flask, render_template, request, url_for
from flask_table import Table, Col
import os
import html
import tablib
import pandas as pd
app = Flask(__name__)

### One Merged Table
@app.route("/")
def show_tables():
    zillow_data = pd.read_csv('zillow.csv')
    census_data = pd.read_csv('census.csv')
    wikipedia_data = pd.read_csv('wikipedia.csv')

    merge_partial = zillow_data.merge(census_data, on='State')
    merged = merge_partial.merge(wikipedia_data, on='State')

    merged.set_index(['State'], inplace=True)
    merged.sort_values('State', inplace=True, ascending=True)

    return render_template('one_table.html',
                            tables=[
                                merged.to_html(),
                            ],
                            titles=[
                                'Merged_Table',
                            ])

#### Three Separate Tables
# @app.route("/")
# def show_tables():
#     zillow_data = pd.read_csv('zillow.csv')
#     census_data = pd.read_csv('census.csv')
#     wikipedia_data = pd.read_csv('wikipedia.csv')

#     #Sort by State alphabetically
#     zillow_data.set_index(['State'], inplace=True)
#     # zillow_data.index.state=None
#     zillow_sorted = zillow_data.sort_values(by=['State'], inplace=False, ascending=True)


#     # data.set_index(['State'], inplace=True)
#     # data.index.state=None

#     # return render_template('index.html',tables=[females.to_html(classes='female'), males.to_html(classes='male')],
#     # titles = ['na', 'Female surfers', 'Male surfers'])
#     page = render_template('index.html',
#                             tables=[
#                                 zillow_sorted.to_html(),
#                                 census_data.to_html(),
#                                 wikipedia_data.to_html(),
#                             ],
#                             titles=[
#                                 'Zillow_Table',
#                                 'Census_Table',
#                                 'Wikipedia_Table',
#                             ])
#     return page

if __name__ == "__main__":
    print('starting Flask app', app.name) 
    app.debug = True
    app.run()