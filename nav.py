import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app

content = html.Div(
    [
        html.Div(className="container", children=[
        html.H1("BDE Manufacturing Report CZ", className="my-4 text-center display-4"),
        dbc.Row(style={"margin-bottom":"25px"},
                children=[
                html.Div(className="col-lg-3", children=[
                        html.Div(className="card h-100 shadow", children=[
                                html.Div(className="card-body", children=[
                                        html.H5(className="card-title", children=[
                                                html.A(href="/apps/Downtime_log", children=[
                                                        html.Div("Downtime log", style={"text-align":"center"}),
                                                ],)
                                        ]),
                                ]),
                        ]),
                ]),
                html.Div(className="col-lg-3", children=[
                        html.Div(className="card h-100 shadow", children=[
                                html.Div(className="card-body", children=[
                                        html.H5(className="card-title", children=[
                                                html.A(href="/apps/Error_log", children=[
                                                        html.Div("Error log", style={"text-align":"center"}),
                                                ],)
                                        ]),
                                ]),
                        ])
                ]),
        ]),
    ],
    id="content"
)

layout = html.Div([content])
