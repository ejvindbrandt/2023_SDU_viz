# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 10:28:57 2023

@author: caspe
"""

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from dash_bootstrap_components import themes

# Put some stuff here to mak layout less busy.
title = "INTERACTIVE MAP OF V-DEM DEMOCRACY INDEX BY COUNTRY"
title_style = {'text_align': 'center'}

# You can replace this with a less.. heavy version of the csv.
df = pd.read_csv("V-Dem-CY-FullOthers_csv_v13/V-Dem-CY-Full+Others-v13.csv")

df = df[df["year"].isin([2022, 2021, 2020, 2019, 2018, 2017, 2016])]
df = df.sort_values(by='year', ascending=False)

#%% so we don't load the csv file again by accident
# Here begins the dash app
app = Dash(__name__, external_stylesheets = [themes.BOOTSTRAP])


app.layout = html.Div([
    html.H1(title, style=title_style),
    html.P("Select a category:"),
    html.Div(
        dcc.RadioItems(
        id='Democracy metric', 
        options=["Total Democracy Score", "Corruption Score", "Turnout"],
        value="Total Democracy Score",
        labelStyle={'display': 'block'}),
        ),
    html.Div(dcc.Graph(id="graph"))
    
], style={"padding-left":"10%"})


@app.callback(
    Output("graph", "figure"), 
    Input("Democracy metric", "value"))
def display_choropleth(value):
    
    if value == "Turnout":
        selected_column = "v2eltrnout"
        legend_title = "Turnout"
    if value == "Corruption Score":
        selected_column = "v2exbribe"
        legend_title = "Corruption"
    if value == "Total Democracy Score":
        selected_column = "v2x_polyarchy"
        legend_title = "Democracy Score"

    fig = px.choropleth(df, 
                        labels={selected_column: legend_title},
                        locations="country_text_id", # the country ISO codes, such as "DNK" for Denmark.
                        locationmode="ISO-3",
                        color=selected_column, # The column that will determine color.
                        hover_name="country_name",
                        hover_data={"v2exnamhos": True, "v2exnamhog": True, "year":True},
                        color_continuous_scale=px.colors.sequential.Plasma[::-1]) # Reverse plasma coloring.
    fig.update_layout(height=900, width=1400)
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                        legend_title + ": %{z}<br>"+
                        "Head of State: %{customdata[0]}<br>" +
                        "Head of Government: %{customdata[1]}<br>"+
                        "Year: %{customdata[2]}<br>" 
    )
    return fig


app.run_server(debug=False)
