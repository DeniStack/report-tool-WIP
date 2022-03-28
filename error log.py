import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import datetime
#import connect
import pandas as pd
from app import app
import mssql_queries
import mssql_conn
import constants
import mysql_queries
import io
import base64

#Here the front-end code starts
controls = dbc.FormGroup(
    [
        dbc.Row([
            dbc.Col(
            html.Div(["Start Time: ", constants.start_date_picker]),
                ),
            dbc.Col(
                    constants.start_time_picker
            )
        ],style={"marginBottom":"0.5em"}),
                dbc.Row([
            dbc.Col(
            html.Div(["End Time: ", constants.end_date_picker]),
                ),
            dbc.Col(
                    constants.end_time_picker
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
    ],style={"marginBottom":"2em"}),
    dbc.Row([
        dbc.Col([
                    html.Div(["Language"])
            ]),
        dbc.Col([
                    constants.language
            ])
    ],style={"marginBottom":"2em"}),
    dbc.Button(
        id='submit_button5',
        n_clicks=0,
        children='Submit',
        color='primary',
        block=True
        ),
    html.Hr(),
    html.Div(id="alert5"),
    html.Div(id="link5")
    ]
)

sidebar = html.Div(
    [
        html.H2('Parameters', style=constants.TEXT_STYLE),
        html.Hr(),
        controls
    ],
    style=constants.SIDEBAR_STYLE,
)

content = html.Div(
    [
        html.H1("Error Log", style={"text-align": "center"}),
        html.Div(id="errors"),
        dcc.Store(id="excel_data5")
    ],
    style=constants.CONTENT_STYLE,
    id="content"
)

layout = html.Div([sidebar, content])

@app.callback(
    [Output("errors", "children"),
    Output("excel_data5", "data"),
    Output("alert5", "children")],
        [Input("submit_button5", "n_clicks")],
        state=[State("start_date_picker", "date"),
        State("start_time_picker", "value"),
        State("end_date_picker", "date"),
        State("end_time_picker", "value"),
        State("database", "value"),
         State("language", "value")]
)
def show_errors(n_clicks, start_date_picker, start_time_picker, end_date_picker, end_time_picker, database, language):
    if n_clicks:
        start_time = datetime.datetime.strptime(start_date_picker, "%Y-%m-%d") + datetime.timedelta(hours=int(start_time_picker[0:2]))
        end_time = datetime.datetime.strptime(end_date_picker, "%Y-%m-%d") + datetime.timedelta(hours=int(end_time_picker[0:2]))
        parameters = [start_time, end_time]

        query_string = mssql_queries.build_db_query_string_app5(str(language))
        records = mssql_conn.execute_query(query_string, parameters, str(database))

        #query_string = mysql_queries.build_db_query_string_app5(str(database), str(language))
        #records = connect.execute_query(query_string, parameters, str(database))
        if records:
            dataframe = pd.DataFrame.from_records(records)
            dataframe.columns = ["ID", "[Alarm text  de-DE , Alarm text]", "Timestamp", "Duration"]
            return dbc.Table.from_dataframe(dataframe), dataframe.to_json(date_format='iso', orient='split'), None
        else:
            return None, None, dbc.Alert("No entries within the specified timeframe.", color="warning", duration=5000)
    else:
        return dbc.Table(None), None, None

@app.callback(Output("link5", "children"),
             [Input("excel_data5", "data")],
            state=[State("start_date_picker", "date"),
            State("start_time_picker", "value"),
            State("end_date_picker", "date"),
            State("end_time_picker", "value"),
            State("database", "value")])
def download_sheet(output, start_date_picker, start_time_picker, end_date_picker, end_time_picker, database):
    if not output:
        return None
    df = pd.read_json(output, orient='split')
    df["Timestamp"] = df["Timestamp"].dt.tz_localize(None)
    start_time = datetime.datetime.strptime(start_date_picker, "%Y-%m-%d") + datetime.timedelta(hours=int(start_time_picker[0:2]))
    end_time = datetime.datetime.strptime(end_date_picker, "%Y-%m-%d") + datetime.timedelta(hours=int(end_time_picker[0:2]))
    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(xlsx_io, engine='xlsxwriter', options={"remove_timezone" : True})
    df.to_excel(writer, sheet_name="Error Log")
    writer.save()
    xlsx_io.seek(0)
    # https://en.wikipedia.org/wiki/Data_URI_scheme
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    data = base64.b64encode(xlsx_io.read()).decode("utf-8")
    href_data_downloadable = f'data:{media_type};base64,{data}'
    file_name = "Error_Log-{0}-{1}_{2}.xlsx".format(str(database), start_time, end_time)
    return html.A("Download Excel Sheet", download=file_name, href=href_data_downloadable)
