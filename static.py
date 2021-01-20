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

divyield = dbc.Card(
    [
        dbc.CardHeader('Yield'),
        dbc.CardBody(
        [
            html.Div('text filler')
        ])
    ],
    outline=True)

pe = dbc.Card(
    [
        dbc.CardHeader('P/E'),
        dbc.CardBody(
        [
            html.Div('text filler')
        ])
    ],
    outline=True)

chowder = dbc.Card(
    [
        dbc.CardHeader('Chowder'),
        dbc.CardBody(
        [
            html.Div('text filler')
        ])
    ],
    outline=True)

fiveten = dbc.Card(
    [
        dbc.CardHeader('5/10 AGR'),
        dbc.CardBody(
        [
            html.Div('text filler')
        ])
    ],
    outline=True)

debtequity = dbc.Card(
    [
        dbc.CardHeader('Debt/Equity'),
        dbc.CardBody(
        [
            html.Div('text filler')
        ])
    ],
    outline=True,
    className='debtequity')

payout = dbc.Card(
    [
        dbc.CardHeader('% Payout'),
        dbc.CardBody(
        [
            html.Div('text filler')
        ])
    ],
    outline=True,
    className='payout')