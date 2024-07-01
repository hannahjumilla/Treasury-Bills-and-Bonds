import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash
import datetime
import plotly.colors as pc
import os


# Initialize the Dash app with callback exception suppression
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.PULSE], suppress_callback_exceptions=True)
app.title = 'T-Bills Dashboard'

# Combined index_string with Lato font and custom styles
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <title>My Dash App</title>
        <link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap" rel="stylesheet">
        {%metas%}
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: #F4F5FE;
                margin: 0;
                height: 100vh;
                display: flex;
                flex-direction: column;
                font-family: 'Lato', sans-serif;
            }
            .content-container {
                flex: 1;
            }
            @keyframes fadeIn {
                0% { opacity: 0; }
                100% { opacity: 1; }
            }
            h1 {
                animation: fadeIn 2s;
            }
            .custom-accordion,
            .custom-accordion-item,
            .custom-accordion-header {
                background-color: #edeef9 !important;
            }
            .custom-accordion .accordion-button:not(.collapsed),
            .custom-accordion .accordion-button:focus {
                background-color: #edeef9 !important;
                border-color: #edeef9 !important;
            }
            .custom-accordion .accordion-body {
                background-color: #edeef9 !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


# Load T-Bills data from CSV
tbills_file_path = "/Users/hannahjumilla/Desktop/Dashboard 2/Tbills3.csv"
df_tbills = pd.read_csv(tbills_file_path)

# Convert 'Date' column to datetime format
df_tbills['Date'] = pd.to_datetime(df_tbills['Date'])

# Load Holders of GS data from CSV
holders_file_path = "/Users/hannahjumilla/Desktop/Dashboard 2/HoldersData.csv"
df_holders = pd.read_csv(holders_file_path)

# Filter out the 'Total' row
df_holders = df_holders[df_holders['Dates'] != 'Total']

# Reshape the holders data to long format
df_holders = df_holders.melt(id_vars=['Dates'], var_name='Date', value_name='Amount')
df_holders['Date'] = pd.to_datetime(df_holders['Date'])

# Load Bonds from the CSV file
tbonds_file_path = '/Users/hannahjumilla/Desktop/Dashboard 2/TreasuryBonds2.csv'
date_parser = lambda x: pd.to_datetime(x, errors='coerce')

# Read the CSV file with specific columns parsed as dates and handle bad lines
df_tbonds = pd.read_csv(tbonds_file_path, parse_dates=[1, 3], date_parser=date_parser, on_bad_lines='skip', encoding='iso-8859-1')

# Ensure 'Series' is treated as a string
df_tbonds['Series'] = df_tbonds['Series'].astype(str)

df_tbonds['Series'] = df_tbonds['Series'].str.replace('.', '-')  # Replace '.' with '-'
df_tbonds['Series'].replace('nan', '', inplace=True)  # Replace 'nan' with empty string or another suitable placeholder

# Replace '25-' with another format that is clearly treated as text
df_tbonds['Series'] = df_tbonds['Series'].str.replace('25-', '25-')

print(df_tbonds['Series'])
print(df_tbonds.iloc[199])

# Define the stoplight component with black background
stoplight_component = html.Div(
    style={'display': 'flex', 'justifyContent': 'left', 'marginTop': '10px'},  # Adjusted marginTop to lower the stoplight
    children=[
        html.Div(
            style={'width': '60px', 'height': '20px', 'display': 'flex', 'justifyContent': 'space-around'},
            children=[
                html.Div(style={'width': '15px', 'height': '15px', 'borderRadius': '50%', 'backgroundColor': 'red'}),
                html.Div(style={'width': '15px', 'height': '15px', 'borderRadius': '50%', 'backgroundColor': 'orange'}),
                html.Div(style={'width': '15px', 'height': '15px', 'borderRadius': '50%', 'backgroundColor': 'green'}),
            ]
        )
    ]
)

# Define the offcanvas navigation menu
offcanvas = dbc.Offcanvas(
    html.Div(
        [
            stoplight_component,
            html.H2(
                "Dashboard",
                style={'color': 'white', 'text-align': 'left', 'marginTop': '0', 'marginLeft': '10px'}
            ),
            html.Hr(style={'background-color': 'white'}),
            dbc.Nav(
                [
                    dbc.NavLink("Home", href="/", active="exact", style={'color': 'white', 'fontSize': '20px'}),
                    dbc.NavLink("Treasury Bills", href="/tbills", active="exact", style={'color': 'white', 'fontSize': '20px'}),
                    dbc.NavLink("Treasury Bonds", href="/tbonds", active="exact", style={'color': 'white', 'fontSize': '20px'}),
                    dbc.NavLink("Holders of Government Securities", href="/holders-of-gs", active="exact", style={'color': 'white', 'fontSize': '20px'}),
                    dbc.NavLink("Market Movers", href="/market-movers", active="exact", style={'color': 'white', 'fontSize': '20px'}),  # New link

                ],
                vertical=True,
                pills=True,
                style={'backgroundColor': 'black', 'height': 'calc(100vh - 150px)', 'overflowY': 'auto'}
            )
        ],
        style={'backgroundColor': 'black', 'padding': '10px', 'height': '100vh', 'display': 'flex', 'flexDirection': 'column'}
    ),
    id="offcanvas",
    is_open=False,
    style={'backgroundColor': 'black'}
)

# Define the top navbar
top_navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "☰",
                            id="open-offcanvas",
                            n_clicks=0,
                            style={'backgroundColor': 'black', 'color': 'white', 'fontSize': '20px', 'border': 'none'}
                        ),
                        width="auto"
                    ),
                    dbc.Col(
                        dbc.NavbarBrand(
                            "Treasury Bills and Bonds Dashboard",
                            style={'color': 'white', 'fontSize': '24px'}
                        )
                    )
                ],
                align="center"
            )
        ],
        fluid=True
    ),
    color="dark",
    dark=True,
    className="mb-4"
)

# Define the layout
app.layout = html.Div(
    style={'backgroundColor': '#F4F5FE', 'minHeight': '100vh'},
    children=[
        top_navbar,
        dbc.Container(
            [
                dcc.Location(id='url', refresh=False),
                html.Div(
                    id='page-content',
                    className='content-container mt-4',
                    style={'textAlign': 'center'},  # Center-align text
                    children=[
                        html.H1("Welcome!", style={'text-align': 'center'}),
                        html.P("About the dashboard"),
                    ]
                )  # Main content area
            ],
            style={'flex': '1'}
        ),
        offcanvas
    ]
)

# Assuming your date parser function is defined correctly elsewhere
date_parser = lambda x: pd.to_datetime(x, errors='coerce')

# Load T-Bills and Bonds data from CSV files
df_tbills = pd.read_csv(tbills_file_path, parse_dates=['Date'], date_parser=date_parser)
df_tbonds = pd.read_csv(tbonds_file_path, parse_dates=['Auction Date'], date_parser=date_parser)

# Filter data to include only entries from 2024
df_tbills_2024 = df_tbills[df_tbills['Date'].dt.year == 2024]
df_tbonds_2024 = df_tbonds[df_tbonds['Auction Date'].dt.year == 2024]

# Calculate total volume awarded for 2024
# Assuming you want to sum across multiple columns for '91-day Volume awarded', '182-day Volume awarded', '364-day Volume awarded'
total_bills_awarded = df_tbills_2024[['91-day Volume awarded', '182-day Volume awarded', '364-day Volume awarded']].sum().sum()
total_bonds_awarded = df_tbonds_2024['Total  Volume Awarded'].sum()
total_bonds_and_bills = total_bills_awarded + total_bonds_awarded

# Assuming you have defined total_bonds_and_bills, total_bills_awarded, and total_bonds_awarded somewhere in your script

# Home Layout
home_layout = html.Div(
    id='page-content',
    className='content-container mt-4',
    children=[
        html.Div(
            style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'position': 'relative', 'marginBottom': '50px'},
            children=[
                html.H1("Welcome", style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'fontSize': '60px'}),
                html.Img(src='/assets/Btr.png', style={'width': '2in', 'position': 'absolute', 'right': '10px', 'top': '0.05cm'})
            ]
        ),
        # Section for Total Bonds and Bills Awarded
        html.Div(
            className='row',
            style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '20px'},
            children=[
                html.Div(
                    className='five columns',
                    style={
                        'backgroundColor': 'white', 
                        'padding': '20px', 
                        'borderRadius': '5px', 
                        'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)', 
                        'width': '5in', 
                        'height': '2in'
                    },
                    children=[
                        html.H3('Total Bonds and Bills Awarded', style={'fontFamily': 'Lato'}),
                        html.H6('for 2024 (in billions)', style={'fontFamily': 'Lato','fontSize': '24px'}),
                        dcc.Graph(
                            id='total-bonds-bills-chart',
                            style={'width': '100%', 'height': '100%'},
                            figure={
                                'data': [
                                    go.Indicator(
                                        mode="number",
                                        value=total_bonds_and_bills,
                                        number={'prefix': 'PHP ', 'valueformat': ','},
                                        domain={'x': [0, 1], 'y': [0.6, 1]}
                                    )
                                ],
                                'layout': {
                                    'title': 'Total Bonds and Bills Awarded for 2024',
                                    'margin': {'l': 30, 'b': 0.5, 'r': 20, 't': 0.1},
                                    'paper_bgcolor': 'transparent',
                                    'plot_bgcolor': 'transparent',
                                    'font': {'color': '#4a4a4a', 'family': 'Lato'}
                                }
                            }
                        )
                    ]
                )
            ]
        ),
        # Section for Total Bills and Total Bonds Awarded
        html.Div(
            className='row',
            style={'display': 'flex', 'justifyContent': 'center', 'marginTop': '0.5in'},  # Adjust marginTop here
            children=[
                html.Div(
                    className='five columns',
                    style={
                        'backgroundColor': 'white', 
                        'padding': '20px', 
                        'borderRadius': '5px', 
                        'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)', 
                        'width': '5in', 
                        'height': '2in', 
                        'marginBottom': '20px',
                        'marginRight': '0.5in'
                    },
                    children=[
                        html.H3('Total Bills Awarded for 2024', style={'fontFamily': 'Lato', 'fontSize': '24px'}),
                        html.H6('(in billions)', style={'fontFamily': 'Lato','fontSize': '24px'}),
                        dcc.Graph(
                            id='total-bills-chart',
                            style={'width': '100%', 'height': '50%'},
                            figure={
                                'data': [
                                    go.Indicator(
                                        mode="number",
                                        value=total_bills_awarded,
                                        number={'prefix': 'PHP ', 'valueformat': ','},
                                        domain={'x': [0, 1], 'y': [1, 0.1]}
                                    )
                                ],
                                'layout': {
                                    'title': 'Total Bills Awarded',
                                    'margin': {'l': 30, 'b': 0.5, 'r': 20, 't': 0.1},
                                    'paper_bgcolor': 'transparent',
                                    'plot_bgcolor': 'transparent',
                                    'font': {'color': '#4a4a4a', 'family': 'Lato'}
                                }
                            }
                        )
                    ]
                ),
                html.Div(
                    className='five columns',
                    style={
                        'backgroundColor': 'white', 
                        'padding': '20px', 
                        'borderRadius': '5px', 
                        'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)', 
                        'width': '5in', 
                        'height': '2in', 
                        'marginBottom': '20px',
                        'marginLeft': '0.5in'
                    },
                    children=[
                        html.H3('Total Bonds Awarded for 2024', style={'fontFamily': 'Lato', 'fontSize': '24px'}),
                        html.H6('(in billions)', style={'fontFamily': 'Lato', 'fontSize': '24px'}),
                        dcc.Graph(
                            id='total-bonds-chart',
                            style={'width': '100%', 'height': '50%'},
                            figure={
                                'data': [
                                    go.Indicator(
                                        mode="number",
                                        value=total_bonds_awarded,
                                        number={'prefix': 'PHP ', 'valueformat': ','},
                                        domain={'x': [0, 1], 'y': [0.6, 0.1]}
                                    )
                                ],
                                'layout': {
                                    'title': 'Total Bonds Awarded',
                                    'margin': {'l': 30, 'b': 0.5, 'r': 20, 't': 0.1},
                                    'paper_bgcolor': 'transparent',
                                    'plot_bgcolor': 'transparent',
                                    'font': {'color': '#4a4a4a', 'family': 'Lato'}
                                }
                            }
                        )
                    ]
                )
            ]
        )
    ],
    style={
        'backgroundColor': '#F4F5FE',  # Background color of the page
        'position': 'relative',
    }
)

#Treasury Bills
tbills_layout = html.Div(
    [
        html.H1("Treasury Bills", style={'text-align': 'center', 'fontFamily': 'Lato', 'fontWeight': 'bold'}),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.Label('Select Tenor', style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black','text-align': 'left'}),
                                        dcc.Dropdown(
                                            id='tbills-tenor-dropdown',
                                            options=[
                                                {'label': '91-day', 'value': '91-day'},
                                                {'label': '182-day', 'value': '182-day'},
                                                {'label': '364-day', 'value': '364-day'}
                                            ],
                                            value='91-day'
                                        ),
                                    ]
                                ),
                            ], className='mb-3'
                        ),
                    ], md=3
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.Label('Select Data', style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black'}),
                                        dcc.Dropdown(
                                            id='tbills-data-dropdown',
                                            value=['91-day Rejection Rate'],  # Initial selection
                                            multi=True
                                        ),
                                    ]
                                ),
                            ], className='mb-3'
                        ),
                    ], md=3
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.Label('Select Stacked Bar Data', style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black'}),
                                        dcc.Dropdown(
                                            id='tbills-stacked-bar-data-dropdown',
                                            options=[
                                                {'label': 'Total  Volume Awarded', 'value': 'Volume awarded'},
                                                {'label': 'Total Volume Tendered', 'value': 'Tenders per tenor'},
                                                {'label': 'Total Offer', 'value': 'Total offers'}
                                            ],
                                            value='Volume awarded'
                                        ),
                                    ]
                                ),
                            ], className='mb-3'
                        ),
                    ], md=3
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.Label('Filter by Month (optional)', style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black'}),
                                        dcc.Dropdown(
                                            id='tbills-month-dropdown',
                                            options=[
                                                {'label': 'January', 'value': 1},
                                                {'label': 'February', 'value': 2},
                                                {'label': 'March', 'value': 3},
                                                {'label': 'April', 'value': 4},
                                                {'label': 'May', 'value': 5},
                                                {'label': 'June', 'value': 6},
                                                {'label': 'July', 'value': 7},
                                                {'label': 'August', 'value': 8},
                                                {'label': 'September', 'value': 9},
                                                {'label': 'October', 'value': 10},
                                                {'label': 'November', 'value': 11},
                                                {'label': 'December', 'value': 12},
                                            ],
                                            multi=True,
                                            placeholder='Select month(s)'
                                        ),
                                    ]
                                ),
                            ], className='mb-3'
                        ),
                    ], md=3
                ),
            ],
            justify='center'  # Center the row contents horizontally
        ),
        html.Label('Select Year Range', style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black'}),
        dcc.RangeSlider(
            id='tbills-year-slider',
            min=df_tbills['Date'].dt.year.min(),
            max=df_tbills['Date'].dt.year.max(),
            value=[df_tbills['Date'].dt.year.min(), df_tbills['Date'].dt.year.max()],
            marks={str(year): str(year) for year in range(df_tbills['Date'].dt.year.min(), df_tbills['Date'].dt.year.max() + 1)},
            step=1
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(id='tbills-graph')
                    ], md=6
                ),
                dbc.Col(
                    [
                        dcc.Graph(id='tbills-stacked-bar-chart')
                    ], md=6
                ),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(id='tbills-combination-chart')
                    ], md=12
                )
            ]
        )
    ],
    className='container',
    style={'fontFamily': 'Lato'}
)

# Define the layout
tbonds_layout = html.Div([
    html.H1("Treasury Bonds", style={'text-align': 'center', 'fontFamily': 'Lato', 'fontWeight': 'bold'}),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label('Select Tenor', style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black'}),
                    dcc.Dropdown(
                        id='tbonds-tenor-dropdown',
                        options=[
                            {'label': '3 years', 'value': 3},
                            {'label': '5 years', 'value': 5},
                            {'label': '7 years', 'value': 7},
                            {'label': '10 years', 'value': 10},
                            {'label': '20 years', 'value': 20},
                            {'label': '25 years', 'value': 25}
                        ],
                        value=3
                    ),
                    html.Label('Select Data for Bar Charts', style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black'}),
                    dcc.Dropdown(
                        id='select-stacked-bar-data-dropdown',
                        options=[
                            {'label': 'Volume Awarded', 'value': 'Total  Volume Awarded'},
                            {'label': 'Volume Tendered', 'value': 'Total Volume Tendered'},
                            {'label': 'Total Offer', 'value': 'Total Offer'}
                        ],
                        value='Total  Volume Awarded'  # Default selection
                    ),
                    html.Label('Select Data for Line Chart', style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black'}),
                    dcc.Dropdown(
                        id='select-line-chart-data-dropdown',
                        options=[
                            {'label': 'Bid-to-Cover', 'value': 'Bid-to-Cover'},
                            {'label': 'WAIR', 'value': 'WAIR'},
                            {'label': 'Rejection Rates', 'value': 'Rejection Rates'}
                        ],
                        value=['Bid-to-Cover'],  # Default selection (multi-select)
                        multi=True  # Allow multi-select
                    ),
                ]),
            ], className='mb-3'),
        ], md=4),  # Left column takes 4 out of 12 columns on medium screens
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label('Select Year Range', style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black'}),
                    dcc.RangeSlider(
                        id='tbonds-year-slider',
                        min=pd.to_datetime(df_tbonds['Auction Date']).dt.year.min(),
                        max=pd.to_datetime(df_tbonds['Auction Date']).dt.year.max(),
                        value=[pd.to_datetime(df_tbonds['Auction Date']).dt.year.min(), pd.to_datetime(df_tbonds['Auction Date']).dt.year.max()],
                        marks={str(year): str(year) for year in range(pd.to_datetime(df_tbonds['Auction Date']).dt.year.min(), pd.to_datetime(df_tbonds['Auction Date']).dt.year.max() + 1)},
                        step=1
                    ),
                    html.Label('Select Month (optional)', style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black'}),
                    dcc.Dropdown(
                        id='tbonds-month-dropdown',
                        options=[
                            {'label': 'January', 'value': 1},
                            {'label': 'February', 'value': 2},
                            {'label': 'March', 'value': 3},
                            {'label': 'April', 'value': 4},
                            {'label': 'May', 'value': 5},
                            {'label': 'June', 'value': 6},
                            {'label': 'July', 'value': 7},
                            {'label': 'August', 'value': 8},
                            {'label': 'September', 'value': 9},
                            {'label': 'October', 'value': 10},
                            {'label': 'November', 'value': 11},
                            {'label': 'December', 'value': 12},
                        ],
                        value=[],  # Default no selection
                        multi=True  # Allow multi-select
                    ),
                    html.Label('Select Date Range for Maturity', style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black'}),
                    dcc.DatePickerRange(
                        id='tbonds-date-picker-range',
                        start_date=pd.to_datetime(df_tbonds['Maturity Date']).min(),
                        end_date=pd.to_datetime(df_tbonds['Maturity Date']).max(),
                        display_format='YYYY',
                        style={'marginTop': '20px'}
                    ),
                ]),
            ], className='mb-3'),
        ], md=8),  # Right column takes 8 out of 12 columns on medium screens
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='stacked-bar-graph'),
        ], md=6),
        dbc.Col([
            dcc.Graph(id='line-chart-graph'),
        ], md=6),
    ], className='mb-3'),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='horizontal-stacked-bar-graph'),
        ], md=6),
        dbc.Col([
            dcc.Graph(id='mature-bonds-bar-graph'),  # New graph for Bonds that will mature
        ], md=6),
    ], className='mb-3'),
], className='container')

# Define the layout for the Holders of GS page
holders_of_gs_layout = html.Div([
    html.H1("Holders of Government Securities", style={'text-align': 'center', 'fontFamily': 'Lato', 'fontWeight': 'bold'}),
    html.H2("(Bonds and Bills)", style={'text-align': 'center'}),
    html.Br(),
    
    # Year Range Slider and Radio Items in the same row
    dbc.Row([
        # Column for Year Range Slider
        dbc.Col([
            html.Label('Select Year Range', style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black'}),
            dcc.RangeSlider(
                id='holders-year-slider',
                min=df_holders['Date'].dt.year.min(),
                max=df_holders['Date'].dt.year.max(),
                value=[df_holders['Date'].dt.year.min(), df_holders['Date'].dt.year.max()],
                marks={str(year): str(year) for year in range(df_holders['Date'].dt.year.min(), df_holders['Date'].dt.year.max() + 1)},
                step=1,
            ),
        ], width=8),  # Adjust width as needed
        
        # Column for Radio Items (Chart Type), aligned to the left
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label('Chart Type', style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black'}),
                    dcc.RadioItems(
                        id='chart-type-radio',
                        options=[
                            {'label': 'Stacked Bar Chart', 'value': 'bar'},
                            {'label': 'Line Chart', 'value': 'line'}
                        ],
                        value='bar',  # Default value
                        labelStyle={'display': 'inline-block', 'margin-right': '10px'}
                    ),
                ]),
            ], style={'width': '100%', 'padding': '10px', 'border': '1px solid #ddd', 'border-radius': '5px'}),
        ], width=4),
    ], style={'margin-bottom': '20px'}),
    
    # Filter by Month Dropdown
    html.Div([
        html.Label('Filter by Month (optional)', style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black'}),
        dcc.Dropdown(
            id='holders-month-dropdown',
            options=[
                {'label': 'January', 'value': 1},
                {'label': 'February', 'value': 2},
                {'label': 'March', 'value': 3},
                {'label': 'April', 'value': 4},
                {'label': 'May', 'value': 5},
                {'label': 'June', 'value': 6},
                {'label': 'July', 'value': 7},
                {'label': 'August', 'value': 8},
                {'label': 'September', 'value': 9},
                {'label': 'October', 'value': 10},
                {'label': 'November', 'value': 11},
                {'label': 'December', 'value': 12},
            ],
            multi=True,
            placeholder='Select month(s)'
        ),
    ]),
    
    html.Br(),
    
    # Loading component wrapping the Graph component
    dcc.Loading(
        id='loading-spinner',
        type='default',  # You can choose different types of spinners
        children=dcc.Graph(id='holders-graph')
    )
], className='container') 

# Get the current date
current_date = datetime.date.today()

# Market Movers Layout
market_movers_layout = html.Div(
    id='page-content',
    className='content-container mt-4',
    children=[
        html.Div(
            style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'position': 'relative', 'marginBottom': '20px'},
            children=[
                html.H1("Market Movers", style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'fontSize': '55px'}),
                html.Img(src='/assets/Btr.png', style={'width': '1.5in', 'position': 'absolute', 'right': '10px', 'top': '0.05cm'}),
            ]
        ),
        html.Div(
            style={'textAlign': 'center', 'marginBottom': '10px'},
            children=[
                html.H2("Latest Updates", style={'textAlign': 'center', 'marginBottom': '25px'})
            ]
        ),
        
        # Scrollable Card Bodies
        html.Div(
            style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'gap': '20px', 'marginTop': '20px'},
            children=[
                html.Div(
                    className='card',
                    style={
                        'backgroundColor': 'white',  # White background
                        'color': 'black',  # Black font color
                        'padding': '20px',
                        'borderRadius': '10px',
                        'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)',
                        'width': '45%',
                        'height': '400px',
                        'overflowY': 'scroll',  # Make card scrollable
                        'textAlign': 'justify'  # Justify content
                    },
                    children=[
                        html.H3("June 2024, Week 3: June 18–19, 2024", style={'color': 'black','textAlign': 'center', 'fontWeight': 'bold'}),
                        html.P("A strong demand was sought for the treasury bills on June 18, almost matching the oversubscription rate of 2.8x last bills auction. The 91D, 182D, and 364D bills attracted average rates of 5.666%, 5.914 percent, and 6.046%, with the auction being oversubscribed by an average of 2.7x the total offer size across all tenors."),
                        html.P("Meanwhile, there was a timid demand for the 20Y bond offered on June 19. The bids came in between 6.720% to 6.820%, which was 4 basis points higher than the range bidded for the 10Y bond offered on June 11. The auction was also oversubscribed by 1.55x the offer size, marking a decent demand for the security. However, it is relatively weaker compared to the demand for the 10Y bond offered the week before, which was oversubscribed by 1.77x."),
                        html.P("This week-on-week change in bond demand may be due to the lack of catalysts that can further drive the bond market. The slightly strong demand for the previous week’s 10Y bond was driven by two factors. First, the softer domestic CPI report showing an increase from 3.8% to 3.9% in May 2024 boosted expectations for a rate cut from BSP. Second, the release of the U.S. labor report caused the U.S. Treasury Yield to soar to 15 bps on June 8. As for the third week of June, market players are still on the lookout for possible macroeconomic catalysts such as the balance of payments and jobless claims data releases. There are also no changes on market expectations on BSP’s policy movement.")
                        # Add your content here
                    ]
                ),
                html.Div(
                    className='card',
                    style={
                        'backgroundColor': 'white',  # White background
                        'color': 'black',  # Black font color
                        'padding': '20px',
                        'borderRadius': '10px',
                        'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)',
                        'width': '45%',
                        'height': '400px',
                        'overflowY': 'scroll',  # Make card scrollable
                        'textAlign': 'justify'  # Justify content
                    },
                    children=[
                        html.H3("June 2024, Week 3: June 25–26, 2024", style={'color': 'black', 'textAlign': 'center','fontWeight': 'bold'}),
                        html.P("The demand for this week’s bill offerings remained strong on June 26, with the bids coming in almost sideways from the previous auction. The 91D, 183D, and 364D bills fetched average rates of 5.666%, 5.930%, and 6.031%, with the auction being oversubscribed by an average of 2.7x the total offer size across all tenors."),
                        html.P("Meanwhile, there was a slightly strong demand for the 20Y bond offered on June 26. The bids came in between 6.800% to 6.900%, which was 7 to 8 basis points higher than the range bidded for the bond offered on June 19 with the same tenor. The auction was also oversubscribed by 1.70x the offer size, which is also stronger than the demand for the 20Y bond offered the week before, which was oversubscribed by 1.54x."),
                        html.P("The market is looking forward to the policy rate decision of the BSP Monetary Board on June 27, with expectations of a hold in its benchmark interest rates amid risks to inflation outlook and weak peso. Market players were also on the lookout for possible macroeconomic catalysts such as the US GDP, US PCE, balance of payments, and jobless claims data releases this week. Additionally, there are geopolitical tensions in the Middle East and heightened Ukrainian drone attacks on Russian refineries, which may inflate price action and stimulate the demand for the USD.")
                        # Add your content here
                    ]
                )
            ]
        ),

        # Cards container
        html.Div(
            style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'gap': '20px', 'marginTop': '20px'},
            children=[
                html.Div(
                    className='card',
                    style={
                        'backgroundColor': 'rgba(0, 0, 0, 0.3)',  # Semi-transparent black background
                        'padding': '20px',
                        'borderRadius': '10px',
                        'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)',
                        'width': '3in',
                        'height': '2in',
                        'textAlign': 'center',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center',
                        'color': 'white'
                    },
                    children=[
                        html.H3("Inflation Rate"),
                        html.P("Content for card 1")
                    ]
                ),
                html.Div(
                    className='card',
                    style={
                        'backgroundColor': 'rgba(0, 0, 0, 0.3)',  # Semi-transparent black background
                        'padding': '20px',
                        'borderRadius': '10px',
                        'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)',
                        'width': '3in',
                        'height': '2in',
                        'textAlign': 'center',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center',
                        'color': 'white'
                    },
                    children=[
                        html.H3("BSP"),
                        html.P("Content for card 2")
                    ]
                ),
                html.Div(
                    className='card',
                    style={
                        'backgroundColor': 'rgba(0, 0, 0, 0.3)',  # Semi-transparent black background
                        'padding': '20px',
                        'borderRadius': '10px',
                        'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)',
                        'width': '3in',
                        'height': '2in',
                        'textAlign': 'center',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center',
                        'color': 'white'
                    },
                    children=[
                        html.H3("Treasury Yields"),
                        html.P("Content for card 3")
                    ]
                ),
                html.Div(
                    className='card',
                    style={
                        'backgroundColor': 'rgba(0, 0, 0, 0.3)',  # Semi-transparent black background
                        'padding': '20px',
                        'borderRadius': '10px',
                        'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)',
                        'width': '3in',
                        'height': '2in',
                        'textAlign': 'center',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center',
                        'color': 'white'
                    },
                    children=[
                        html.H3("Federal Rates"),
                        html.P("Content for card 4")
                    ]
                ),
            ]
        ),

        # FAQs and Calendar container
        html.Div(
            style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'start', 'marginTop': '40px'},
            children=[
                html.Div(
                    style={'width': '60%'},
                    children=[
                        html.H2("FAQs", style={'textAlign': 'left', 'marginTop': '40px'}),
                        dbc.Accordion(
                            [
                                dbc.AccordionItem(
                                    title="What is the Bid-to-cover Ratio?",
                                    children=[
                                        html.P("The Bid-to-cover Ratio is a measure of demand for treasury securities...")
                                    ],
                                    className='custom-accordion-item'
                                ),
                                dbc.AccordionItem(
                                    title="What is the WAIR?",
                                    children=[
                                        html.P("The Weighted Average Interest Rate (WAIR) is a calculation used to determine the overall rate of return on a portfolio of debt securities...")
                                    ],
                                    className='custom-accordion-item'
                                ),
                                dbc.AccordionItem(
                                    title="What is the Rejection Rate?",
                                    children=[
                                        html.P("The Rejection Rate refers to the percentage of bids that are rejected in a treasury auction...")
                                    ],
                                    className='custom-accordion-item'
                                ),
                            ],
                            start_collapsed=True,
                            className='custom-accordion'
                        )
                    ]
                ),
                html.Div(
                    style={'width': '35%'},
                    children=[
                        html.H2("Calendar", style={'textAlign': 'left', 'marginTop': '40px'}),
                        dcc.DatePickerRange(
                            id='date-picker-range',
                            start_date=current_date.replace(day=1),
                            end_date=current_date,
                            display_format='MMMM D, YYYY',
                            start_date_placeholder_text='Start Date',
                            end_date_placeholder_text='End Date',
                            calendar_orientation='vertical',
                            style={
                                'backgroundColor': 'rgba(0, 0, 0, 0.05)',  # Light background for calendar
                                'padding': '20px',
                                'borderRadius': '10px',
                                'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)',
                                'width': '100%'
                            },
                        )
                    ]
                )
            ]
        )
    ],
    style={
        'backgroundColor': '#F4F5FE',  # Background color of the page
        'position': 'relative',
    }
)
# Callback to update T-Bills data dropdown based on selected tenor
@app.callback(
    Output('tbills-data-dropdown', 'options'),
    [Input('tbills-tenor-dropdown', 'value')]
)
def update_tbills_data_dropdown(selected_tenor):
    if selected_tenor == '91-day':
        return [
            {'label': '91-day Rejection Rate', 'value': '91-day Rejection Rate'},
            {'label': '91-day Wair', 'value': '91-day Wair'},
            {'label': '91-day Bid-to-cover', 'value': '91-day Bid-to-cover'}
        ]
    elif selected_tenor == '182-day':
        return [
            {'label': '182-day Rejection Rate', 'value': '182-day Rejection Rate'},
            {'label': '182-day Wair', 'value': '182-day Wair'},
            {'label': '182-day Bid-to-cover', 'value': '182-day Bid-to-cover'}
        ]
    elif selected_tenor == '364-day':
        return [
            {'label': '364-day Rejection Rate', 'value': '364-day Rejection Rate'},
            {'label': '364-day Wair', 'value': '364-day Wair'},
            {'label': '364-day Bid-to-cover', 'value': '364-day Bid-to-cover'}
        ]
    else:
        return []

# Callback to update T-Bills graph, stacked bar chart, and combination chart
@app.callback(
    [Output('tbills-graph', 'figure'),
     Output('tbills-stacked-bar-chart', 'figure'),
     Output('tbills-combination-chart', 'figure')],
    [Input('tbills-tenor-dropdown', 'value'),
     Input('tbills-year-slider', 'value'),
     Input('tbills-data-dropdown', 'value'),
     Input('tbills-month-dropdown', 'value'),
     Input('tbills-stacked-bar-data-dropdown', 'value')]
)
def update_tbills_graph(selected_tenor, selected_year, selected_data, selected_months, selected_stacked_bar_data):
    print(f"Selected Tenor: {selected_tenor}")
    print(f"Selected Year: {selected_year}")
    print(f"Selected Data: {selected_data}")
    print(f"Selected Months: {selected_months}")
    print(f"Selected Stacked Bar Data: {selected_stacked_bar_data}")

    # Filter DataFrame based on year
    filtered_df = df_tbills[(df_tbills['Date'].dt.year >= selected_year[0]) &
                            (df_tbills['Date'].dt.year <= selected_year[1])]

    # Filter DataFrame based on month if selected
    if selected_months:
        filtered_df = filtered_df[filtered_df['Date'].dt.month.isin(selected_months)]

    print(f"Filtered DataFrame:\n{filtered_df.head()}")

    # Create figure for line graph
    fig = go.Figure()
    if selected_data:
        for data in selected_data:
            print(f"Accessing column: {data}")
            if data in filtered_df.columns:
                mode = 'lines'
                if 'Bid-to-cover' in data:
                    mode = 'lines+markers'
                fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df[data],
                                         mode=mode, name=data,
                                         marker=dict(symbol='diamond'),
                                         connectgaps=True))  # Ensure lines are connected even with gaps
            else:
                print(f"Warning: Column '{data}' does not exist in the DataFrame")

    # Update layout for line graph
    title_text = ', '.join(selected_data) if selected_data else ''
    fig.update_layout(
        title=dict(
            text=f'{title_text} {selected_year[0]}-{selected_year[1]}',
            x=0.5,
            xanchor='center',
            font=dict(
                size=18,
                color='black',
                family='Lato, Arial, sans-serif'
            )
        ),
        xaxis=dict(
            title=dict(
                text='Date',
                font=dict(
                    size=18,
                    color='black',
                    family='Lato, Arial, sans-serif'
                )
            )
        ),
        yaxis=dict(
            title=dict(
                text='Rate',
                font=dict(
                    size=18,
                    color='black',
                    family='Lato, Arial, sans-serif'
                )
            )
        )
    )

    # Create figure for stacked bar chart
    bar_fig = go.Figure()
    if selected_stacked_bar_data:
        bar_column = f'{selected_tenor} {selected_stacked_bar_data}'
        print(f"Accessing column: {bar_column}")
        if bar_column in filtered_df.columns:
            bar_fig.add_trace(go.Bar(x=filtered_df['Date'], y=filtered_df[bar_column], name=bar_column))
        else:
            print(f"Warning: Column '{bar_column}' does not exist in the DataFrame")

    # Update layout for stacked bar chart
    bar_title_text = f'{selected_stacked_bar_data} {selected_tenor} {selected_year[0]}-{selected_year[1]}' if selected_stacked_bar_data else ''
    bar_fig.update_layout(
        barmode='stack',
        title=dict(
            text=bar_title_text,
            x=0.5,
            xanchor='center',
            font=dict(
                size=24,
                color='black',
                family='Lato, Arial, sans-serif'
            )
        ),
        xaxis=dict(
            title=dict(
                text='Date',
                font=dict(
                    size=18,
                    color='black',
                    family='Lato, Arial, sans-serif'
                )
            )
        ),
        yaxis=dict(
            title=dict(
                text='Volume',
                font=dict(
                    size=18,
                    color='black',
                    family='Lato, Arial, sans-serif'
                )
            )
        )
    )

    # Create figure for combination chart
    combo_fig = go.Figure()
    if selected_data:
        for data in selected_data:
            print(f"Accessing column: {data}")
            if data in filtered_df.columns:
                combo_fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df[data],
                                               mode='lines', name=data,
                                               connectgaps=True))  # Ensure lines are connected even with gaps
            else:
                print(f"Warning: Column '{data}' does not exist in the DataFrame")

    if selected_stacked_bar_data:
        bar_column = f'{selected_tenor} {selected_stacked_bar_data}'
        print(f"Accessing column: {bar_column}")
        if bar_column in filtered_df.columns:
            combo_fig.add_trace(go.Bar(x=filtered_df['Date'], y=filtered_df[bar_column], name=bar_column))

    # Update layout for combination chart
    combo_title_text = ', '.join(selected_data) if selected_data else ''
    combo_fig.update_layout(
        title=dict(
            text=f'{combo_title_text} {selected_stacked_bar_data} {selected_year[0]}-{selected_year[1]}',
            x=0.5,
            xanchor='center',
            font=dict(
                size=24,
                color='black',
                family='Lato, Arial, sans-serif'
            )
        ),
        xaxis=dict(
            title=dict(
                text='Date',
                font=dict(
                    size=18,
                    color='black',
                    family='Lato, Arial, sans-serif'
                )
            )
        ),
        yaxis=dict(
            title=dict(
                text='Value',
                font=dict(
                    size=18,
                    color='black',
                    family='Lato, Arial, sans-serif'
                )
            )
        )
    )

    return fig, bar_fig, combo_fig

# Callback to update vertical stacked bar chart
@app.callback(
    Output('stacked-bar-graph', 'figure'),
    [Input('tbonds-tenor-dropdown', 'value'),
     Input('tbonds-year-slider', 'value'),
     Input('tbonds-month-dropdown', 'value'),
     Input('select-stacked-bar-data-dropdown', 'value')]
)
def update_stacked_bar_graph(selected_tenor, selected_year, selected_month, selected_data):
    if selected_month is None:
        selected_month = []

    filtered_df = df_tbonds[
        (pd.to_datetime(df_tbonds['Auction Date']).dt.year >= selected_year[0]) &
        (pd.to_datetime(df_tbonds['Auction Date']).dt.year <= selected_year[1]) &
        (df_tbonds['Tenor (in years)'] == selected_tenor)
    ]

    if selected_month:
        filtered_df = filtered_df[pd.to_datetime(filtered_df['Auction Date']).dt.month.isin(selected_month)]

    fig = go.Figure()

    if selected_data is not None:  # Add a check for None here
        if isinstance(selected_data, list):
            for data in selected_data:
                hover_texts = []
                for index, row in filtered_df.iterrows():
                    hover_text = f'Series: {row["Series"]} - Auction Date: {row["Auction Date"].strftime("%Y-%m-%d")}<br>{data}: {row[data]}'
                    hover_texts.append(hover_text)

                fig.add_trace(go.Bar(
                    x=filtered_df['Auction Date'],
                    y=filtered_df[data],
                    name=data,
                    hovertext=hover_texts,
                    hoverinfo='text+y'
                ))
        else:
            hover_texts = []
            for index, row in filtered_df.iterrows():
                hover_text = f'Series: {row["Series"]} - Auction Date: {row["Auction Date"].strftime("%Y-%m-%d")}<br>{selected_data}: {row[selected_data]}'
                hover_texts.append(hover_text)

            fig.add_trace(go.Bar(
                x=filtered_df['Auction Date'],
                y=filtered_df[selected_data],
                name=selected_data,
                hovertext=hover_texts,
                hoverinfo='text+y'
            ))

        fig.update_layout(
            title=dict(
                text=f'<b>{selected_data}</b> - Tenor: {selected_tenor} years',
                x=0.5,
                xanchor='center',
                font=dict(
                    size=24,
                    color='black',
                    family='Lato, Arial, sans-serif'
                )
            ),
            xaxis=dict(
                title=dict(
                    text='Auction Date',
                    font=dict(
                        size=18,
                        color='black',
                        family='Lato, Arial, sans-serif'
                    )
                )
            ),
            yaxis=dict(
                title=dict(
                    text='Value',
                    font=dict(
                        size=18,
                        color='black',
                        family='Lato, Arial, sans-serif'
                    )
                )
            ),
            barmode='stack',
            hoverlabel=dict(
                font=dict(
                    size=12,
                    family='Lato, Arial, sans-serif'
                )
            )
        )
    else:
        # Handle case where selected_data is None or invalid
        fig.update_layout(
            title="Select a Data Field",
            xaxis=dict(
                title=dict(
                    text='Auction Date',
                    font=dict(
                        size=18,
                        color='black',
                        family='Lato, Arial, sans-serif'
                    )
                )
            ),
            yaxis=dict(
                title=dict(
                    text='Value',
                    font=dict(
                        size=18,
                        color='black',
                        family='Lato, Arial, sans-serif'
                    )
                )
            ),
            barmode='stack',
            hoverlabel=dict(
                font=dict(
                    size=12,
                    family='Lato, Arial, sans-serif'
                )
            )
        )

    return fig
# Callback to update line chart
@app.callback(
    Output('line-chart-graph', 'figure'),
    [Input('tbonds-tenor-dropdown', 'value'),
     Input('tbonds-year-slider', 'value'),
     Input('tbonds-month-dropdown', 'value'),
     Input('select-line-chart-data-dropdown', 'value')]
)
def update_line_chart(selected_tenor, selected_year, selected_month, selected_data):
    if selected_month is None:
        selected_month = []

    filtered_df = df_tbonds[
        (pd.to_datetime(df_tbonds['Auction Date']).dt.year >= selected_year[0]) &
        (pd.to_datetime(df_tbonds['Auction Date']).dt.year <= selected_year[1]) &
        (df_tbonds['Tenor (in years)'] == selected_tenor)
    ]

    if selected_month:
        filtered_df = filtered_df[pd.to_datetime(filtered_df['Auction Date']).dt.month.isin(selected_month)]

    fig = go.Figure()

    if isinstance(selected_data, list):
        for data in selected_data:
            # Filter out blank values in the selected data column
            filtered_data = filtered_df[data].dropna()
            fig.add_trace(go.Scatter(
                x=filtered_df.loc[filtered_data.index, 'Auction Date'],
                y=filtered_data,
                mode='lines+markers',
                name=data
            ))
    else:
        # Filter out blank values in the selected data column
        filtered_data = filtered_df[selected_data].dropna()
        fig.add_trace(go.Scatter(
            x=filtered_df.loc[filtered_data.index, 'Auction Date'],
            y=filtered_data,
            mode='lines+markers',
            name=selected_data
        ))

    fig.update_layout(
        title=dict(
            text=f'<b>{", ".join(selected_data)}</b> - Tenor: {selected_tenor} years',
            x=0.5,
            xanchor='center',
            font=dict(
                size=24,
                color='black',
                family='Lato, Arial, sans-serif'
            )
        ),
        xaxis=dict(
            title=dict(
                text='Auction Date',
                font=dict(
                    size=18,
                    color='black',
                    family='Lato, Arial, sans-serif'
                )
            )
        ),
        yaxis=dict(
            title=dict(
                text='Value',
                font=dict(
                    size=18,
                    color='black',
                    family='Lato, Arial, sans-serif'
                )
            )
        ),
        showlegend=True,
        legend=dict(
            x=0,
            y=1,
            font=dict(
                family='Lato, Arial, sans-serif'
            )
        )
    )

    return fig

# Callback to update horizontal stacked bar chart
@app.callback(
    Output('horizontal-stacked-bar-graph', 'figure'),
    [Input('tbonds-tenor-dropdown', 'value'),
     Input('tbonds-year-slider', 'value'),
     Input('tbonds-month-dropdown', 'value'),
     Input('select-stacked-bar-data-dropdown', 'value')]
)
def update_horizontal_stacked_bar_graph(selected_tenor, selected_year, selected_month, selected_data):
    if selected_month is None:
        selected_month = []

    filtered_df = df_tbonds[
        (pd.to_datetime(df_tbonds['Auction Date']).dt.year >= selected_year[0]) &
        (pd.to_datetime(df_tbonds['Auction Date']).dt.year <= selected_year[1]) &
        (df_tbonds['Tenor (in years)'] == selected_tenor)
    ]

    if selected_month:
        filtered_df = filtered_df[pd.to_datetime(filtered_df['Auction Date']).dt.month.isin(selected_month)]

    fig = go.Figure()

    if isinstance(selected_data, list):
        for data in selected_data:
            hover_texts = []
            for index, row in filtered_df.iterrows():
                hover_text = f'Series: {str(row["Series"])} - Auction Date: {row["Auction Date"].strftime("%Y-%m-%d")}<br>{data}: {row[data]}'
                hover_texts.append(hover_text)

            fig.add_trace(go.Bar(
                y=filtered_df['Series'].astype(str),  # Ensure 'Series' is treated as string
                x=filtered_df[data],
                orientation='h',
                name=data,
                hovertext=hover_texts,
                hoverinfo='text+x'
            ))
    else:
        hover_texts = []
        for index, row in filtered_df.iterrows():
            hover_text = f'Series: {str(row["Series"])} - Auction Date: {row["Auction Date"].strftime("%Y-%m-%d")}<br>{selected_data}: {row[selected_data]}'
            hover_texts.append(hover_text)

        fig.add_trace(go.Bar(
            y=filtered_df['Series'].astype(str),  # Ensure 'Series' is treated as string
            x=filtered_df[selected_data],
            orientation='h',
            name=selected_data,
            hovertext=hover_texts,
            hoverinfo='text+x'
        ))

    fig.update_layout(
        title=dict(
            text=f'<b>{selected_data}</b> - Tenor: {selected_tenor} years',
            x=0.5,
            xanchor='center',
            font=dict(
                size=24,
                color='black',
                family='Lato, Arial, sans-serif'
            )
        ),
        xaxis_title=dict(
            text='Value',
            font=dict(
                size=18,
                color='black',
                family='Lato, Arial, sans-serif'
            )
        ),
        yaxis_title=dict(
            text='Series',
            font=dict(
                size=18,
                color='black',
                family='Lato, Arial, sans-serif'
            )
        ),
        barmode='stack',
        yaxis=dict(
            type='category',  # Explicitly set y-axis type to 'category'
            tickfont=dict(family='Lato, Arial, sans-serif')
        ),
        hoverlabel=dict(
            font_size=12,  # Adjust the font size as needed
            font_family='Lato, Arial, sans-serif'
        )
    )

    return fig

# Load Bonds from the CSV file
@app.callback(
    Output('mature-bonds-bar-graph', 'figure'),
    [
        Input('tbonds-date-picker-range', 'start_date'),
        Input('tbonds-date-picker-range', 'end_date')
    ]
)
def update_mature_bonds_chart(start_date, end_date):
    filtered_data = df_tbonds.copy()
    
    # Convert start_date and end_date to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter by date range
    filtered_data = filtered_data[
        (pd.to_datetime(filtered_data['Maturity Date']) >= start_date) &
        (pd.to_datetime(filtered_data['Maturity Date']) <= end_date)
    ]

    # Ensure 'Series' is treated as string
    filtered_data['Series'] = filtered_data['Series'].astype(str)
    
    # Convert dates to datetime
    filtered_data['Maturity Date'] = pd.to_datetime(filtered_data['Maturity Date'])
    filtered_data['Auction Date'] = pd.to_datetime(filtered_data['Auction Date'])

    # Sort data by Maturity Date
    filtered_data = filtered_data.sort_values(by='Maturity Date')

    # Check if there's any data to plot
    if filtered_data.empty:
        return go.Figure()

    # Create hover texts for bar chart
    hover_texts = [
        f'Series: {row["Series"]} - Auction Date: {row["Auction Date"].strftime("%Y-%m-%d")} - Maturity Date: {row["Maturity Date"].strftime("%Y-%m-%d")}'
        for _, row in filtered_data.iterrows()
    ]

    # Calculate durations for the bars
    duration_years = (filtered_data['Maturity Date'] - filtered_data['Auction Date']).dt.days / 365

    # Create horizontal bar chart
    fig = go.Figure()

    # Add bars for the duration from issuance to maturity
    fig.add_trace(go.Bar(
        y=filtered_data['Series'],
        x=duration_years,
        base=filtered_data['Auction Date'].dt.year,
        orientation='h',
        name='Duration to Maturity',
        hovertext=hover_texts,
        hoverinfo='text+x'
    ))

    fig.update_layout(
        title=dict(
            text=f'<b>Bond Maturity Distribution</b> ({start_date.year} to {end_date.year})',
            x=0.5,
            xanchor='center',
            font=dict(
                size=24,
                color='black',
                family='Lato, Arial, sans-serif'
            )
        ),
        xaxis_title=dict(
            text='Year',
            font=dict(
                size=18,
                color='black',
                family='Lato, Arial, sans-serif'
            )
        ),
        yaxis_title=dict(
            text='Series Name',
            font=dict(
                size=18,
                color='black',
                family='Lato, Arial, sans-serif'
            )
        ),
        xaxis=dict(
            type='linear',
            tick0=start_date.year,
            dtick=1,
            range=[start_date.year, end_date.year]
        ),
        yaxis=dict(
            type='category',  # Explicitly set y-axis type to 'category'
            tickfont=dict(family='Lato, Arial, sans-serif')
        ),
        hoverlabel=dict(
            font_size=12,  # Adjust the font size as needed
            font_family='Lato, Arial, sans-serif'
        )
    )

    return fig



# Callback to update the Holders of GS graph
@app.callback(
    Output('holders-graph', 'figure'),
    [Input('holders-year-slider', 'value'),
     Input('holders-month-dropdown', 'value'),
     Input('chart-type-radio', 'value')]
)
def update_holders_graph(selected_year, selected_months, chart_type):
    filtered_df = df_holders[(df_holders['Date'].dt.year >= selected_year[0]) &
                             (df_holders['Date'].dt.year <= selected_year[1])]
    
    if selected_months:
        filtered_df = filtered_df[filtered_df['Date'].dt.month.isin(selected_months)]
    
    # Debugging: Check if the DataFrame is empty after filtering
    if filtered_df.empty:
        print("Filtered DataFrame is empty")
    
    fig = go.Figure()
    
    colors = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99',
              '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a',
              '#ffff99', '#b15928', '#000000']
    
    if chart_type == 'bar':
        # Create stacked bar chart
        holders = filtered_df['Dates'].unique()
        holders = sorted(holders)
        
        color_map = {holder: colors[i % len(colors)] for i, holder in enumerate(holders)}
        
        grouped = filtered_df.groupby('Date')
        
        for date, group in grouped:
            sorted_group = group.sort_values(by='Amount', ascending=False)
            for i, (_, row) in enumerate(sorted_group.iterrows()):
                fig.add_trace(go.Bar(
                    x=[date],
                    y=[row['Amount']],
                    name=row['Dates'],
                    marker_color=color_map[row['Dates']]
                ))
        
        fig.update_layout(
            barmode='stack',
            title=dict(
                text=f'<b>Holders of GS {selected_year[0]}-{selected_year[1]}</b>',
                x=0.5,
                xanchor='center',
                font=dict(
                    size=24,
                    color='black',
                    family='Lato, Arial, sans-serif'
                )
            ),
            xaxis_title=dict(
                text='Date',
                font=dict(
                    size=18,
                    color='black',
                    family='Lato, Arial, sans-serif'
                )
            ),
            yaxis_title=dict(
                text='Amount',
                font=dict(
                    size=18,
                    color='black',
                    family='Lato, Arial, sans-serif'
                )
            ),
            legend=dict(title='Holders', traceorder='normal'),
            showlegend=True,
            hoverlabel=dict(
                font_size=12,  # Adjust the font size as needed
                font_family='Lato, Arial, sans-serif'
            )
        )
        
    elif chart_type == 'line':
        # Create line chart
        for holder in filtered_df['Dates'].unique():
            temp_df = filtered_df[filtered_df['Dates'] == holder]
            fig.add_trace(go.Scatter(
                x=temp_df['Date'],
                y=temp_df['Amount'],
                mode='lines',
                name=holder,
                line=dict(color=colors[len(fig.data) % len(colors)])
            ))
        
        fig.update_layout(
            title=dict(
                text=f'<b>Holders of GS {selected_year[0]}-{selected_year[1]}</b>',
                x=0.5,
                xanchor='center',
                font=dict(
                    size=24,
                    color='black',
                    family='Lato, Arial, sans-serif'
                )
            ),
            xaxis_title=dict(
                text='Date',
                font=dict(
                    size=18,
                    color='black',
                    family='Lato, Arial, sans-serif'
                )
            ),
            yaxis_title=dict(
                text='Amount',
                font=dict(
                    size=18,
                    color='black',
                    family='Lato, Arial, sans-serif'
                )
            ),
            legend=dict(title='Holders', traceorder='normal'),
            showlegend=True,
            hoverlabel=dict(
                font_size=12,  # Adjust the font size as needed
                font_family='Lato, Arial, sans-serif'
            )
        )
    
    return fig

    
# Callback to toggle offcanvas
@app.callback(
    Output("offcanvas", "is_open"),
    [Input("open-offcanvas", "n_clicks")],
    [dash.dependencies.State("offcanvas", "is_open")]
)
def toggle_offcanvas(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open



# Update the display_page callback
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/tbills':
        return tbills_layout
    elif pathname == '/tbonds':
        return tbonds_layout
    elif pathname == '/holders-of-gs':
        return holders_of_gs_layout
    elif pathname == '/market-movers':
        return market_movers_layout
    else:
        return home_layout

# Run the app on port 8051 instead of the default 8050
if __name__ == '__main__':
    app.run_server(debug=True, port=8052)

               


  







































