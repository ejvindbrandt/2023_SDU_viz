# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 19:34:36 2023

@author: caspe
"""
""" THIS VERSION INCLUDES:
        SOME RESTRUCTURING (WIP, FEEDBACK THX)
        TIME RANGE SLIDER
        COMPARISON TOOL REWORK (MULTI SELECT)
        REGION SELECT
        COULD NOT MAKE ICONS ON MAP WORK YET BUT MAYBE POsSIBLE TO COMBINE CHOROPLETH WITH SCATTER
            (BOTTOM PAGE)
        SOME OTHER STUFF. 

"""

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# Put some stuff here to mak layout less busy.
title = "INTERACTIVE MAP OF V-DEM DEMOCRACY INDEX BY COUNTRY"
title_style = {"text_align": "left"}

# You can replace this with a less.. heavy version of the csv.
df = pd.read_csv("V-Dem-CD_csv_v13/V-Dem-CD-v13.csv")
df = df[["year",  # The desired columns from the csv.
         "country_text_id", 
         "country_name", 
         "v2eltrnout",
         "v2exbribe",
         "v2x_polyarchy",
         "v2exnamhos",
         "v2exnamhog"
         ]]

df = df[df["year"].isin(range(2000, 2023 + 1))] # Desired year range.
df = df.sort_values(by="year", ascending=False) # Sorting by latest year first.

#%% so we don"t load the csv file again by accident
# Here begins the dash app
app = Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])


app.layout = dbc.Container([
    
    # Main Title
    dbc.Row(
        html.H1(title),
        ),
    
    
    html.Br(),
    
    # The Choropleth Map Row
    dbc.Row([
        dbc.Col([
            html.P("Select a Metric"),
            # Metric Selector
            dcc.Dropdown(
                id="Democracy metric", 
                options=["Democracy Score", "Corruption Score", "Turnout"],
                value="Democracy Score"
            ),
            html.Br(),
            html.Br(),
            # Region Selector
            html.P("Select a Region"),
            dcc.Dropdown(
                id="regions", 
                options=["World", "Europe", "Asia", "Africa", "North America", "South America"],
                value="World"
            ),
            
            html.Br(),
            html.Br(),
            
            html.Div(id="test"),
            ], width=2),
        # Choropleth Map
        dbc.Col(html.Div(dcc.Graph(id="choropleth")), width=10),
        
        
            
    ]),
    
    # Click country graph & other 
    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(id="select_country_graph"))),
        dbc.Col(html.Div(id="test_thingy"))
    ]),
    
    
    
    
    # Comparison Tool
    dbc.Row([
        html.P("Comparison Tool"),
        dcc.Dropdown(
        id="multi_compare", 
        options=[{"label": country, "value": country} for country in df["country_name"].drop_duplicates()], # Removes duplicate country entries
        value=["Denmark", "South Korea"], multi=True), # Multi allows for multiple selections.
        ]),
    
    # Compare Graph
    dbc.Row(
        dcc.Graph(id="compare_graph"),
    ),
    
    # Slider based on year for comparison
    dbc.Row([
        html.P("Year Range Slider"),
        dcc.RangeSlider(id="slider", min=0, max=23, step=1, value=[0, 23]),
    ]),
    
    # A scatter plot using data from the df and in-built iso data. Colored based on difference in democracy score right now.
    dcc.Graph(id='test_scatter'),
    
])


@app.callback(
    Output("select_country_graph", "figure"),
    Output("test_thingy", "children"),
    Input("Democracy metric", "value"),
    Input("choropleth", "clickData"),
    )

def update_comparison(selected_metric, selected_country):
    if selected_metric == "Turnout":
        selected_column = "v2eltrnout"
        legend_title = "Turnout"
    elif selected_metric == "Corruption Score":
        selected_column = "v2exbribe"
        legend_title = "Lack of Corruption"
    elif selected_metric == "Democracy Score":
        selected_column = "v2x_polyarchy"
        legend_title = "Democracy Score"
    

        
    
    if selected_country is not None:
        country_iso = selected_country["points"][0]["location"]
        country_name = df.loc[df["country_text_id"] == country_iso, "country_name"].iloc[0]
        fig_selected_country = px.bar(
            df[df["country_text_id"] == country_iso].groupby("year")[selected_column].mean().reset_index(),
            x="year",  
            y=selected_column,    
            title=f"{legend_title}: {country_name}",
        )
        
    else:
        country_iso = "DNK"
        fig_selected_country = px.bar(
            df[df["country_text_id"] == country_iso],
            x="year",  
            y=selected_column, 
            title=f"{legend_title}: Denmark",
        )    
        fig_selected_country.update_layout(
            xaxis_title="Years 2000-2023", 
            yaxis_title=legend_title
        )    
        
        
    # This is just calculating the difference between first recorded year and last.
    drop_nan = df.loc[df[selected_column].notna()]
    last_val = drop_nan.loc[(df["country_text_id"] == country_iso), ["year", selected_column]].sort_values("year", ascending=False).iloc[0][selected_column]
    init_val = drop_nan.loc[(df["country_text_id"] == country_iso), ["year", selected_column]].sort_values("year").iloc[0][selected_column]
    print(last_val)
    print(init_val)
    difference = round((last_val - init_val), 3)

    return fig_selected_country, difference

@app.callback(
    Output("choropleth", "figure"),
    Input("Democracy metric", "value"),
    Input("regions", "value"),
    )

def display_choropleth(selected_metric, selected_region):
    if selected_metric == "Turnout":
        selected_column = "v2eltrnout"
        legend_title = "Turnout"
    elif selected_metric == "Corruption Score":
        selected_column = "v2exbribe"
        legend_title = "Lack of Corruption"
    elif selected_metric == "Democracy Score":
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
                        color_continuous_scale=px.colors.sequential.Plasma[::-1], # Reverse plasma coloring.
                        scope=selected_region.lower(), # Determines region selected.
    )

    
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
        # Projection type. There are a bunch, look at the link.
        projection_type="natural earth",
        
        # Color statements.
        coastlinecolor="Black",
        landcolor="white",
        countrycolor="white",
        oceancolor="LightBlue",
        
        # Various show-this-or-that statements.
        showcoastlines=True,
        showland=True,
        showcountries=True,
        showocean=True,
        showlakes=False,
        showframe=True,
    )
    
    choro_fig.update_layout(
        dragmode=False, # Prevents the user from "grabbing" and rotating the world. 
                        # Felt this feature was laggy and unnecessary.
        coloraxis_colorbar=dict( # Settings for the choropleth color bar.
            len=0.7,
            thickness=20,
            title=""
        ),
        margin=dict(l=0, r=0, t=0, b=0), # Sets the inside margins of the choropleth box.
        height=600, # This only accepts pixel values. Maybe possible to adapt to user screen size with javascript.
    )
    
    return choro_fig



@app.callback(
    Output("compare_graph", "figure"),
    Input("Democracy metric", "value"),
    Input("multi_compare", "value"),
    Input("slider", "value"),
)

def update_comparison_slider(selected_metric, compare, slider):
    
    if selected_metric == "Turnout":
        selected_column = "v2eltrnout"
        legend_title = "Turnout"
    elif selected_metric == "Corruption Score":
        selected_column = "v2exbribe"
        legend_title = "Lack of Corruption"
    elif selected_metric == "Democracy Score":
        selected_column = "v2x_polyarchy"
        legend_title = "Democracy Score"
    
    
    # Comparison tool
    
    # This is just 
    if slider[0] <10:
        slider[0] = int("200" + str(slider[0]))
    else:
        slider[0] = int("20" + str(slider[0]))
    if slider[1] <10:
        slider[1] = int("200" + str(slider[1]))
    else:
        slider[1] = int("20" + str(slider[1]))    
    
    
    slider_df = df[df["country_name"].isin(compare)]
    slider_df = slider_df[slider_df["year"].between(slider[0], slider[1])]
    
    
    fig_comparison = px.bar(
        slider_df,
        x="year",
        y=selected_column,
        color="country_name",
        barmode="group",  
    )
    
    
    fig_comparison.update_layout(
        xaxis_title="Years 2000-2023", 
        yaxis_title=legend_title
    )
    
    
    
    return fig_comparison


# This callback is just for testing the hover. 
# I was thinking of implementing a highlight, but that seemed a little hard.
@app.callback(
    Output("test", "children"),
    Input("choropleth", "hoverData"),
)

def do_something(hovering):
    
    if hovering:
        iso = hovering['points'][0]["hovertext"]

        return iso
    else:
        return no_update
    
        
@app.callback(
    Output("test_scatter", "figure"),
    Input("Democracy metric", "value")
)

def scatter_do(hover_data):
    df['increased'] = df['v2x_polyarchy'].diff() > 0
    scatter_icons = go.Figure(go.Scattergeo(
        locations=df['country_text_id'],
        text=df['country_name'],
        marker=dict(
            color=df['increased'].map({True: "green", False: "red"}),
            size=5,
            symbol='circle',
            opacity=0.7,
        ),
        mode='markers'
    ))
    
    scatter_icons.update_geos(
        # Projection type. There are a bunch, look at the link.
        projection_type="natural earth",
        visible=False
    )
    
    
    scatter_icons.update_layout(
        dragmode=False, # Prevents the user from "grabbing" and rotating the world. 
                        # Felt this feature was laggy and unnecessary.
        coloraxis_colorbar=dict( # Settings for the choropleth color bar.
            len=0.7,
            thickness=20,
            title=""
        ),
        margin=dict(l=0, r=0, t=0, b=0), # Sets the inside margins of the choropleth box.
        height=600, # This only accepts pixel values. Maybe possible to adapt to user screen size with javascript.
    )
    
    
    return scatter_icons
    
app.run_server(debug=False) # Can also set to true, but doesn"t work for me for some reason.