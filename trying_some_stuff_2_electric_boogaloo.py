# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 04:58:42 2023

@author: caspe
"""

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Put some stuff here to mak layout less busy.
title = "INTERACTIVE MAP OF V-DEM DEMOCRACY INDEX BY COUNTRY"
title_style = {"text_align": "center"}

# You can replace this with a less.. heavy version of the csv.
df = pd.read_csv("V-Dem-CD_csv_v13/V-Dem-CD-v13.csv")
df = df[["year", 
         "country_text_id", 
         "country_name", 
         "v2eltrnout",
         "v2exbribe",
         "v2x_polyarchy",
         "v2exnamhos",
         "v2exnamhog"
         ]]

df = df[df["year"].isin(range(2000, 2023 + 1))]
df = df.sort_values(by="year", ascending=False)

#%% so we don"t load the csv file again by accident
# Here begins the dash app
app = Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])


app.layout = dbc.Container([
    dbc.Row(
        html.H1(title, style=title_style),
        ),
    dbc.Row([
        html.P("Select a category:"),
        html.Div(
            dcc.Dropdown(
            id="Democracy metric", 
            options=["Total Democracy Score", "Corruption Score", "Turnout"],
            value="Total Democracy Score",),
            ),
        ]),
    html.Br(),
    dbc.Row([
        html.P("Comparison Tool"),
        dbc.Col(
            dcc.Dropdown(
            id="country_compare_1", 
            options=[{"label": country, "value": country} for country in df["country_name"].drop_duplicates()],
            value="Denmark",),
            ),
        dbc.Col(
            dcc.Dropdown(
            id="country_compare_2", 
            options=[{"label": country, "value": country} for country in df["country_name"].drop_duplicates()],
            value="Germany",),
            ),
        ]),
    
    dbc.Row(
        dcc.Graph(id="compare_graph"),
        ),
    
    dbc.Row([
        dbc.Col([html.Div(dcc.Graph(id="graph"))
            ], width=9),
        dbc.Col([html.Div(dcc.Graph(id="graph3"))
            ], width=3),
        ]),
    dbc.Row([html.Div(dcc.Graph(id="graph2"))
        ]),
    
    
    
    
    ])



@app.callback(
    Output("graph", "figure"),
    Output("graph2", "figure"),
    Output("graph3", "figure"),
    Output("compare_graph", "figure"),
    Input("Democracy metric", "value"),
    Input("graph", "clickData"),
    Input("country_compare_1", "value"),
    Input("country_compare_2", "value")
    )
def display_choropleth(map_settings, selected_country, compare1, compare2):
    if map_settings == "Turnout":
        selected_column = "v2eltrnout"
        legend_title = "Turnout"
    elif map_settings == "Corruption Score":
        selected_column = "v2exbribe"
        legend_title = "Lack of Corruption"
    elif map_settings == "Total Democracy Score":
        selected_column = "v2x_polyarchy"
        legend_title = "Democracy Score"

    # Main choropleth graph
    choro_fig = px.choropleth(df, 
                        labels={selected_column: legend_title},
                        locations="country_text_id", # the country ISO codes, such as "DNK" for Denmark.
                        locationmode="ISO-3",
                        color=selected_column, # The column that will determine color.
                        hover_name="country_name",
                        hover_data={"v2exnamhos": True, "v2exnamhog": True, "year":True},
                        color_continuous_scale=px.colors.sequential.Plasma[::-1]) # Reverse plasma coloring.
    #choro_fig.update_layout(height=900, width=1400)
    choro_fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                        legend_title + ": %{z}<br>"+
                        "Head of State: %{customdata[0]}<br>" +
                        "Head of Government: %{customdata[1]}<br>"+
                        "Year: %{customdata[2]}<br>" 
    )
    
    
    # Apparently a lot of different settings available via this update_geos thing.
    # We should look into that a bit more. https://plotly.com/python/reference/layout/geo/
    choro_fig.update_geos(
        projection_type="natural earth",
        showcoastlines=True,
        coastlinecolor="Black",
        showland=True,
        landcolor="white",
        showocean=True,
        oceancolor="LightBlue",
        showcountries=True,
        countrycolor="Black",
        showframe=False,
    )
    
    # Second graph, should probably rename. Purpose: Not sure.
    fig2 = px.bar(
        df.sort_values(by=selected_column, ascending=False),
        x="country_text_id", 
        y=selected_column,   
        title="All Countries",
    )
    
    # Third graph, should probably rename. Purpose: Info when clicking on a country.
    
    fig3 = px.bar(
        df[df["country_text_id"] == "DNK"],
        x="year",  
        y=selected_column, 
        title=f"Barchart of {legend_title} for Denmark",
    )
    
    
    if selected_country is not None:
        country_iso = selected_country["points"][0]["location"]
        country_name = df.loc[df['country_text_id'] == country_iso, 'country_name'].iloc[0]
        fig3 = px.bar(
            df[df["country_text_id"] == country_iso],
            x="year",  
            y=selected_column,    
            title=f"Barchart of {legend_title} for {country_name}",
        )
    
    
        
    # Comparison tool
    
    fig4 = px.bar(
        df[df["country_name"].isin([compare1, compare2])],
        x="year",
        y=selected_column,
        color="country_name",
        barmode="group",  
    )
    
    for figs in [fig2, fig3, fig4]: # Purpose: labelling the charts.
        figs.update_layout(
        xaxis_title="Years 2000-2023", 
        yaxis_title=legend_title
    )
    
    return choro_fig, fig2, fig3, fig4


app.run_server(debug=False)
