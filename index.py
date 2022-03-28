import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app
from apps import app1, app2,
import nav

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == "/":
        return nav.layout
    elif pathname == '/apps/downtime':
        #app.title = "Downtime and Reasons"
        return app1.layout
    elif pathname == "/apps/error log":
        #app.title = "Report of Check Criteria"
        return app2.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
    #app.run_server(host="10.3.41.18", port=8080, debug=False)
