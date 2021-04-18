import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from style import CARD_STYLE


def generate_bar_chart(data_dict):
    x, y = [data_dict[key] for key in data_dict], [key for key in data_dict]
    return go.Figure(go.Bar(
        x=x,
        y=y,
        orientation='h'))


def generate_card(title, graph):
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4(title, className="card-title"),
                    graph
                ]
            ),
        ],
        style=CARD_STYLE,
    )


navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(dbc.NavbarBrand("COVID-19 Twitter Sentiment Analysis", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
            href="#",
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
    ],
    color="dark",
    dark=True,
)

data_table = dbc.Card([
    html.H4("Tweet Data", className="card-title"),
    dash_table.DataTable(
        id='tweet-table',
        columns=[{'id': col_name, 'name': col_name} for col_name in ['tweet', 'polarity', 'fetched_at',
                                                                     'dashboard_time', 'recv_time']],
        filter_action='native',
        sort_action='native',
    )
],
    body=True
)
