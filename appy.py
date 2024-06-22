import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State  
import plotly.colors as pc

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
tbills_file_path = "/Users/hannahjumilla/Desktop/Dashboard 2/Tbills.csv"
df_tbills = pd.read_csv(tbills_file_path)

# Load Holders of GS data from CSV
holders_file_path = "/Users/hannahjumilla/Desktop/Dashboard 2/Cleaned_Holders_Data.csv"
df_holders = pd.read_csv(holders_file_path)

# Load Treasury Bonds data from CSV
tbonds_file_path = "/Users/hannahjumilla/Desktop/Dashboard 2/Tbonds.csv"
df_tbonds = pd.read_csv(tbonds_file_path, parse_dates=['Auction Date'])

# Convert 'Date' column to datetime format
df_tbills['Date'] = pd.to_datetime(df_tbills['Date'])


# Filter out the 'Total' row
df_holders = df_holders[df_holders['Dates'] != 'Total']

# Reshape the holders data to long format
df_holders = df_holders.melt(id_vars=['Dates'], var_name='Date', value_name='Amount')
df_holders['Date'] = pd.to_datetime(df_holders['Date'])

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


# Define the layout for the home page
home_layout = html.Div(
    id='page-content',
    className='content-container mt-4',
    children=[
        html.H1("Welcome!", style={'text-align': 'center', 'fontFamily': 'Lato', 'fontWeight': 'bold'}),
        html.H2("About the dashboard"),
    ],
    style={
        'backgroundColor': '#F4F5FE',  # Changed background color
    }
)
# Define your existing layout for Treasury Bills
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
                    ], md=4
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
                    ], md=4
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
                    ], md=4
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
                    ], md=8
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H3("Latest News on Treasury Bills", className="card-title", style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black'}),
                                        html.Div(
                                            [
                                                html.P("News item 1", style={'fontFamily': 'Lato'}),
                                                html.P("News item 2", style={'fontFamily': 'Lato'}),
                                                html.P("News item 3", style={'fontFamily': 'Lato'}),
                                                html.P("News item 4", style={'fontFamily': 'Lato'}),
                                                html.P("News item 5", style={'fontFamily': 'Lato'}),
                                                html.P("News item 6", style={'fontFamily': 'Lato'}),
                                                html.P("News item 7", style={'fontFamily': 'Lato'}),
                                                html.P("News item 8", style={'fontFamily': 'Lato'}),
                                                html.P("News item 9", style={'fontFamily': 'Lato'}),
                                                html.P("News item 10", style={'fontFamily': 'Lato'}),
                                            ],
                                            style={'maxHeight': '400px', 'overflowY': 'scroll', 'padding': '10px'}
                                        ),
                                    ]
                                ),
                            ],
                            style={'background-color': '#edeef9', 'height': '500px', 'overflowY': 'auto'}
                        ),
                    ], md=4
                ),
            ]
        )
    ],
    className='container',
    style={'fontFamily': 'Lato'}
)

# Treasury Bonds layout
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
                ]),
            ], className='mb-3'),
            dbc.Card([
                dbc.CardBody([
                    html.Label('Select Data', style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black'}),
                    dcc.Dropdown(
                        id='tbonds-data-dropdown',
                        value=['Bid-to-Cover'],  # Initial selection
                        multi=True
                    ),
                ]),
            ], className='mb-3'),
            dbc.Card([
                dbc.CardBody([
                    html.Label('Select Year Range', style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black'}),
                    dcc.RangeSlider(
                        id='tbonds-year-slider',
                        min=df_tbonds['Auction Date'].dt.year.min(),
                        max=df_tbonds['Auction Date'].dt.year.max(),
                        value=[df_tbonds['Auction Date'].dt.year.min(), df_tbonds['Auction Date'].dt.year.max()],
                        marks={str(year): str(year) for year in range(df_tbonds['Auction Date'].dt.year.min(), df_tbonds['Auction Date'].dt.year.max() + 1)},
                        step=1
                    ),
                ]),
            ], className='mb-3'),
            html.Br(),
            dcc.Graph(id='tbonds-graph')
        ], md=8),  # Left side content takes 8 out of 12 columns on medium screens
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label('Latest News on Bonds', style={'fontFamily': 'Lato', 'fontWeight': 'bold', 'color': 'black'}),
                    html.Div([
                        html.P(
                            "With Beijing set to overhaul its monetary tools by restarting treasury bonds purchases in the secondary markets, China’s central bank and finance ministry are expected to dovetail efforts to support the economy as fiscal policies take on a crucial role, according to a former People’s Bank of China official. Sheng Songcheng, the former chief of the PBOC’s statistics department, also said that conditions, including the sheer size and liquidity of China’s bond market, are ripe for the central bank to trade bonds in the secondary markets to inject money to aid the economy. His remarks at the annual Lujiazui Forum in Shanghai on Thursday came after PBOC governor Pan Gongsheng confirmed for the first time on Wednesday that discussions between the central bank and Ministry of Finance to end a two-decade hiatus on bond trading had taken place, following an order by President Xi Jinping at October’s twice-a-decade central financial work conference."
                        )
                    ], style={'max-height': '300px', 'overflow-y': 'auto', 'padding-right': '15px'})  # Adjust padding-right for scrollbar width consideration
                ]),
            ], className='mb-3', style={'background-color': '#edeef9', 'padding': '15px', 'height': '100%'}),
        ], md=4),  # Right side sidebar takes 4 out of 12 columns on medium screens
    ]),
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
    
# Callback to update Treasury Bonds data dropdown based on selected tenor
@app.callback(
    Output('tbonds-data-dropdown', 'options'),
    [Input('tbonds-tenor-dropdown', 'value')]
)
def update_tbonds_data_dropdown(selected_tenor):
    options = [
        {'label': 'Bid-to-Cover', 'value': 'Bid-to-Cover'},
        {'label': 'WAIR', 'value': 'WAIR'},
        {'label': 'Rejection Rates', 'value': 'Rejection Rates'}
    ]
    return options

# Callback to update the T-Bills graph
@app.callback(
    Output('tbills-graph', 'figure'),
    [Input('tbills-tenor-dropdown', 'value'),
     Input('tbills-year-slider', 'value'),
     Input('tbills-data-dropdown', 'value'),
     Input('tbills-month-dropdown', 'value')]
)
def update_tbills_graph(selected_tenor, selected_year, selected_data, selected_months):
    filtered_df = df_tbills[(df_tbills['Date'].dt.year >= selected_year[0]) &
                            (df_tbills['Date'].dt.year <= selected_year[1])]
    
    if selected_months:
        filtered_df = filtered_df[filtered_df['Date'].dt.month.isin(selected_months)]
    
    fig = go.Figure()
    
    for data in selected_data:
        mode = 'lines'
        if 'Bid-to-cover' in data:
            mode = 'lines+markers'
        fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df[data],
                                 mode=mode, name=data,
                                 marker=dict(symbol='diamond')))
    
    # Determine y-axis tick values and format
    min_y = filtered_df[selected_data].min().min()  # Minimum value in selected data
    max_y = filtered_df[selected_data].max().max()  # Maximum value in selected data
    
    # Handle the case where there is no data or all NaNs
    if pd.isna(min_y) or pd.isna(max_y):
        min_y = 0
        max_y = 10  # Adjust as needed based on your data
    
    # Calculate y-axis tick values ensuring intervals of 10
    yaxis_tickvals = list(range(int(min_y) - (int(min_y) % 10), int(max_y) + 10, 10))
    
    # Generate title based on selected data and years
    selected_data_title = ', '.join(selected_data) if selected_data else 'T-Bill Data'
    year_range = f'{selected_year[0]}-{selected_year[1]}'
    title = f'{selected_data_title}  {year_range}' if selected_data_title else f'T-Bill Rates {year_range}'
    
    fig.update_layout(title=title,
                      xaxis_title='Date',
                      yaxis_title='Rate',
                      yaxis_tickvals=yaxis_tickvals)
    
    fig.update_traces(connectgaps=True)  # Ensure lines are connected despite NA values

    return fig

# Callback to update the Treasury Bonds graph
@app.callback(
    Output('tbonds-graph', 'figure'),
    [Input('tbonds-tenor-dropdown', 'value'),
     Input('tbonds-year-slider', 'value'),
     Input('tbonds-data-dropdown', 'value')]
)
def update_tbonds_graph(selected_tenor, selected_year, selected_data):
    filtered_df = df_tbonds[(df_tbonds['Auction Date'].dt.year >= selected_year[0]) &
                            (df_tbonds['Auction Date'].dt.year <= selected_year[1]) &
                            (df_tbonds['Tenor (in years)'] == selected_tenor)]
    
    fig = go.Figure()
    
    for data in selected_data:
        mode = 'lines'
        if data == 'Bid-to-Cover':
            mode = 'lines+markers'
        fig.add_trace(go.Scatter(x=filtered_df['Auction Date'], y=filtered_df[data],
                                 mode=mode, name=data,
                                 marker=dict(symbol='diamond') if data == 'Bid-to-Cover' else None))
    
    fig.update_layout(title=f'Treasury Bonds {selected_tenor}-year Tenor',
                      xaxis_title='Auction Date',
                      yaxis_title='Value')
    
    fig.update_traces(connectgaps=True)  # Ensure lines are connected despite NA values

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
            title=f'Holders of GS {selected_year[0]}-{selected_year[1]}',
            xaxis_title='Date',
            yaxis_title='Amount',
            legend=dict(title='Holders', traceorder='normal'),
            showlegend=True
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
            title=f'Holders of GS {selected_year[0]}-{selected_year[1]}',
            xaxis_title='Date',
            yaxis_title='Amount',
            legend=dict(title='Holders', traceorder='normal'),
            showlegend=True
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
    elif pathname == '/holders-of-gs':
        return holders_of_gs_layout
    elif pathname == '/tbonds':
        return tbonds_layout
    else:
        return home_layout
    

# Run the app on port 8051 instead of the default 8050
if __name__ == '__main__':
    app.run_server(debug=True)


               


  







































