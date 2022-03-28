from pandas.core.frame import DataFrame
from apps.app1 import convert_timedelta_int, input_check_cycle_time_and_efficiency
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import datetime
#import connect
import pandas as pd
from app import app
from datetime import datetime as dt
from datetime import timedelta
import dash
import plotly.graph_objects as go
import distutils.dist
import utils
import constants
import mssql_queries
import mssql_conn
import mysql_queries
import base64
import io
import flask 
import os
import sys
from waitress import serve
import json
#import kaleido
import plotly
import base64
from app import app
import utils
import mysql_queries
import mssql_queries
import mssql_conn
import constants
import pyodbc
import plotly.express as px


controls = dbc.FormGroup(
    [
        dbc.Row([
            dbc.Col(
            html.Div(["Start Time: ", constants.start_date_picker],
                    ),
                ),
            dbc.Col(
                html.Div([ constants.start_time_picker ])
            )
        ],style={"marginBottom":"0.5em"}),
                dbc.Row([
            dbc.Col(
            html.Div(["End Time: ", constants.end_date_picker]),
                ),
            dbc.Col(constants.end_time_picker 
                ),
        ]),
     html.Hr(),
    dbc.Row([
         dbc.Col([
                     html.Div(["Database"])
             ]),
         dbc.Col([
                     constants.database
             ])
     ],style={"marginBottom":"1em"}),          
    dbc.Row([
    ],style={"marginBottom":"1em"}),
    dbc.Row([
        dbc.Col([
                    html.Div(["Language"])
            ]),
        dbc.Col([
                    constants.language
            ])
    ],style={"marginBottom":"0.5em"}),
    html.Hr(),
    dbc.Button(
        id='submit_button',
        n_clicks=0,
        children='Submit',
        color='primary',
        block=True
        ),
    html.Hr(),
    html.Div(id="alert7"),#appcallback output 3
    html.Div(id="link7"),#appcallback  download sheet output
    html.Div(id="link8")
    ]
)

sidebar = html.Div(
    [
        html.H2('Input', style=constants.TEXT_STYLE),
        # html.H3('Parameters', style=constants.TEXT_STYLE),
        html.Hr(),
        controls
    ],
    style=constants.SIDEBAR_STYLE,
)

content = html.Div(
    [
        dcc.Tabs([
            dcc.Tab(label='Report', children=[
                dcc.Store(id="downtime_data"),#appcallback output 2
                html.Div(id="downtime", style={"display" : "none"}),
                html.Div(id="report_downtime"),#appcallback output 1
                dcc.Store(id="excel_data7"),
                dcc.Store(id="Bar_chart_link"),#appcallback pie output 3
                html.Div(id="table1"),
                html.Hr(),
                dbc.Row([
                ],style={"marginBottom":"0.5em"}),
            ]),
        dcc.Tab(label='Daily', children=[
                dcc.Graph(id="bar_chart7", style={"height":800}),#appcallback pie output 1
                dcc.Store(id="excel_data7"),
            ]),
            dcc.Tab(label='Weekly', children=[
                dcc.Graph(id="bar_chart2", style={"height":800}),#appcallback pie output 1
                dcc.Store(id="excel_data7"),
            ]),
        ]),
    ],
    style=constants.CONTENT_STYLE,
    id="content"
)



layout = html.Div([sidebar, content])



@app.callback([
    Output("report_downtime", "children"),
    Output("downtime_data", "data"),
    Output("alert7", "children"),
    Output("excel_data7", "data"),#output za excel download 

    ],
        # Ide sve sto vidimo sa lijeve strane ispod parametara,to se samo nadodaje to je ustavri sad input informacija
        [Input("submit_button", "n_clicks")],
        state=[State("start_date_picker", "date"),
        State("start_time_picker", "value"),
        State("end_date_picker", "date"),
        State("end_time_picker", "value"),
        State("database", "value"),
        State("language", "value")]
)
        
def fetch_the_downtime(n_clicks, start_date_picker, start_time_picker, end_date_picker, end_time_picker, database, language):
    if n_clicks:
        start_time = datetime.datetime.strptime(start_date_picker, "%Y-%m-%d") + datetime.timedelta(hours=int(start_time_picker[0:2]))
        end_time = datetime.datetime.strptime(end_date_picker, "%Y-%m-%d") + datetime.timedelta(hours=int(end_time_picker[0:2]))
        parameters = [start_time, end_time]

        query_string = mssql_queries.build_db_query_app7()
        records = mssql_conn.execute_query(query_string, parameters, str(database))
        

        if records:
            dataframe = pd.DataFrame.from_records(records)
            dataframe.columns = ["ID", "Timestamp", "Duration", "Week Number"]
            dataframe['Duration'] = dataframe['Duration'].astype('datetime64[s]').dt.strftime("%H:%M:%S")#pretvoriti u minute

   


            return dbc.Table.from_dataframe(dataframe), dataframe.to_json(date_format="iso", orient="split"), None, dataframe.to_json(date_format='iso', orient='split')#ovo zadnje za excel download button
        else:
            return None, None, dbc.Alert("No entries within the specified timeframe.", color="warning", duration=5000), dataframe.to_json(date_format='iso', orient='split')
    else:
        return dbc.Table(None), None, None, None





@app.callback(
    Output("bar_chart7", "figure"),
    [Input("downtime_data", "data")],
    state=[State("start_date_picker", "date"),
    State("start_time_picker", "value"),
    State("end_date_picker", "date"),
    State("end_time_picker", "value"),
    State("database", "value"),
    State("language", "value")]
)
def create_bar_chart(n_clicks, start_date_picker, start_time_picker, end_date_picker, end_time_picker, database, language):
    if n_clicks:
        start_time = datetime.datetime.strptime(start_date_picker, "%Y-%m-%d") + datetime.timedelta(hours=int(start_time_picker[0:2]))
        end_time = datetime.datetime.strptime(end_date_picker, "%Y-%m-%d") + datetime.timedelta(hours=int(end_time_picker[0:2]))
        parameters = [start_time, end_time]
    

        query_string = mssql_queries.build_db_query_app7()
        records = mssql_conn.execute_query(query_string, parameters, str(database))


        if records:
            dataframe = pd.DataFrame.from_records(records)
            dataframe.columns = ["ID", "Timestamp", "Duration", "Week Number"]
           
            dataframe['Timestamp'] = pd.to_datetime(dataframe['Timestamp']).dt.date
            dataframe = dataframe.groupby("Timestamp")['Duration'].sum().reset_index()


            print("--dataframe--")
            
            print(dataframe)
            
            print(dataframe)
            print("---")           
          

            
            fig = px.bar(dataframe, x=dataframe['Timestamp'], y=dataframe['Duration'], title=("Downtime in minutes:") + ' ' + (database))
            fig.update_xaxes(
                dtick="D1",
                tickformat="%d-%m-%Y",
            )

            
            return  go.Figure(fig)
        else:
            fig = {}
    else:
        fig = {}
            


@app.callback(
    Output("bar_chart2", "figure"),
    [Input("downtime_data", "data")],
    state=[State("start_date_picker", "date"),
    State("start_time_picker", "value"),
    State("end_date_picker", "date"),
    State("end_time_picker", "value"),
    State("database", "value"),
    State("language", "value")]
)
def create_bar_chart_weekly(n_clicks, start_date_picker, start_time_picker, end_date_picker, end_time_picker, database, language):
    if n_clicks:
        start_time = datetime.datetime.strptime(start_date_picker, "%Y-%m-%d") + datetime.timedelta(hours=int(start_time_picker[0:2]))
        end_time = datetime.datetime.strptime(end_date_picker, "%Y-%m-%d") + datetime.timedelta(hours=int(end_time_picker[0:2]))
        parameters = [start_time, end_time]

        query_string = mssql_queries.build_db_query_app7()
        records = mssql_conn.execute_query(query_string, parameters, str(database))


        if records:
            dataframe = pd.DataFrame.from_records(records)
            dataframe.columns = ["ID", "Timestamp", "Duration", "Week Number"]
           
            dataframe['Timestamp'] = pd.to_datetime(dataframe['Timestamp']).dt.date
            dataframe = dataframe.groupby("Week Number")['Duration'].sum().reset_index()
      
            print("--dataframe--")
          
            print(dataframe)
        
            print(dataframe)
            print("---")   
         
            fig = px.bar(dataframe, x=dataframe['Week Number'], y=dataframe['Duration'], title=("Downtime in minutes: ") + ' ' + (database))
            
           
            return  go.Figure(fig)
            
        else:
            fig = {} 
    else:
        fig = {}


@app.callback(Output("link7", "children"),
             [Input("excel_data7", "data")],
            state=[State("start_date_picker", "date"),
            State("start_time_picker", "value"),
            State("end_date_picker", "date"),
            State("end_time_picker", "value"),
            State("database", "value")])
def download_sheet(output, start_date_picker, start_time_picker, end_date_picker, end_time_picker, database):
    if not output:
        return None
    df = pd.read_json(output, orient='split')
    df["Timestamp"] = df["Timestamp"].dt.tz_localize(None)#ovdje bi umjesto Timestamp mogli staviti DATE 
    start_time = datetime.datetime.strptime(start_date_picker, "%Y-%m-%d") + datetime.timedelta(hours=int(start_time_picker[0:2]))
    end_time = datetime.datetime.strptime(end_date_picker, "%Y-%m-%d") + datetime.timedelta(hours=int(end_time_picker[0:2]))
    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(xlsx_io, engine='xlsxwriter', options={"remove_timezone" : True})
    df.to_excel(writer, sheet_name="Downtime Log")
    writer.save()
    xlsx_io.seek(0)
    # https://en.wikipedia.org/wiki/Data_URI_scheme
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    data = base64.b64encode(xlsx_io.read()).decode("utf-8")
    href_data_downloadable = f'data:{media_type};base64,{data}'
    file_name = "Downtime_Log-{0}-{1}_{2}.xlsx".format(str(database), str(start_time), str(end_time))
    return html.A("Downtime Raw Sheet", download=file_name, href=href_data_downloadable)

@app.callback(Output("link8", "children"),
            [Input("excel_data_error_log", "data")],
            state=[State("start_date_picker", "date"),
            State("start_time_picker", "value"),
            State("end_date_picker", "date"),
            State("end_time_picker", "value"),
            State("database", "value")])
def download_sheet(output, output2, output3, start_date_picker, start_time_picker, end_date_picker, end_time_picker, database):
    if not output:
        return None
    df = pd.read_json(output, orietn='split').reset_index(drop=True)
    df2 = pd.read_json(output2, orient='split').reset_index(drop=True)
    df3 = pd.read_json(output3, orient='split')
    df["Timestamp"] = df["Timestamp"].dt.tz_localize(None)
    start_time = datetime.datetime.strptime(start_date_picker, "%Y-%m-%d") + datetime.timedelta(hours=int(start_time_picker[0:2]))
    end_time = datetime.datetime.strptime(end_date_picker, "%Y-%m-%d") + datetime.timedelta(hours=int(end_time_picker[0:2]))
    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(xlsx_io, engine="xlswriter", options={"remove_timezone" : True})
    df.to_excel(writer, sheet_name="Log Report")
    df2.to_excel(writer, sheet_name="Daily Data")
    df3.to_excel(writer, sheet_name="Weekly Data")
    writer.save()
    xlsx_io.seek(0)
    # https://en.wikipeadia.org/wiki/Data_URL_scheme
    media_type = 'application/vnd.openxlmformats-officedocument.spreadsheethtml.sheet'
    data =  base64.b64encode(xlsx_io.read()).decode("utf-8")
    href_data_downloadable = f'data:{media_type};base64,{data}'
    file_name= "Downtime_Log-{0}-{1}_{2}.xlsx".format(str(database), str(start_time), str(end_time))
    return html.A("Download Excel Sheet", download=file_name, href=href_data_downloadable)
