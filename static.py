import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc


dropdown = dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'New York City', 'value': 'NYC'},
            {'label': 'Montreal', 'value': 'MTL'},
            {'label': 'San Francisco', 'value': 'SF'}
        ],
        value='NYC'
    )

company_name = dbc.Card(
    [
        dbc.CardHeader('Company Name'),
        dbc.CardBody(
        [
            html.Div('text filler')
        ])
    ],
    outline=True)