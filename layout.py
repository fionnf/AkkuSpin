from dash import html, dcc


def create_layout():
    return html.Div([
    html.Div([
        html.H1("AkkuSpin",
                style={'font-family': 'Arial, sans-serif', 'text-align': 'center', 'padding': '20px 0',
                       'color': 'white'}),
    ], style={'background-color': '#0047AB', 'color': 'white', 'margin': '0', 'padding': '0'}),

    # Interval component for live updates
    dcc.Interval(
        id='interval-component',
        interval=120 * 1000,  # in milliseconds (5 seconds here)
        n_intervals=0
    ),

    html.Div([
        html.Div([
            html.Label("NMR Folder Path:", style={'font-family': 'Arial, sans-serif', 'font-size': '16px'}),
            dcc.Input(id='nmr_folder_input', type='text', placeholder='Enter NMR Folder Path',
                      value=r'Test\NMR Folder',
                      style={'width': '80%', 'font-family': 'Arial, sans-serif', 'border': 'none', 'color': 'black',
                             'background-color': '#EDEDED'}),
        ], style={'display': 'inline-block'}),

        html.Div([
            html.Label("Voltage Folder Path:", style={'font-family': 'Arial, sans-serif', 'font-size': '16px'}),
            dcc.Input(id='voltage_folder_input', type='text', placeholder='Enter Voltage Folder Path',
                      value=r'Test\Cyclerfolder',
                      style={'width': '80%', 'font-family': 'Arial, sans-serif', 'border': 'none', 'color': 'black',
                             'background-color': '#EDEDED'}),
        ], style={'display': 'inline-block'}),

        html.Div([
            dcc.RadioItems(
                id='nmr_format_selector',
                options=[
                    {'label': 'Bruker', 'value': 'Bruker'},
                    {'label': 'Varian', 'value': 'Varian'}
                ],
                value='Varian',
                labelStyle={'display': 'inline-block'},
                style={'font-family': 'Arial, sans-serif', 'font-size': '14px'}
            )
        ])
    ], style={'margin': '0'}),

    html.Div([
        html.Div([
            html.H2("NMR Spectra and Voltage Trace", style={'font-family': 'Arial, sans-serif'}),

            html.Label("Min PPM:", style={'font-family': 'Arial, sans-serif'}),
            dcc.Input(id='ppm_min_input', type='number', placeholder='Min PPM', value=-58.75,
                      style={'width': '20%', 'font-family': 'Arial, sans-serif', 'border': 'none', 'color': 'black',
                             'background-color': '#EDEDED', 'margin-right': '10px'}),

            html.Label("Max PPM:", style={'font-family': 'Arial, sans-serif'}),
            dcc.Input(id='ppm_max_input', type='number', placeholder='Max PPM', value=-57.25,
                      style={'width': '20%', 'font-family': 'Arial, sans-serif', 'border': 'none', 'color': 'black',
                             'background-color': '#EDEDED'}),

            html.Label(" Nucleus:", style={'font-family': 'Arial, sans-serif'}),
            dcc.RadioItems(
                id='nucleus_selector',
                options=[
                    {'label': '1H', 'value': '1H'},
                    {'label': '19F', 'value': '19F'}
                ],
                value='19F',
                labelStyle={'display': 'inline-block'},
                style={'font-family': 'Arial, sans-serif', 'display': 'inline-block'}
            ),

        ], style={'display': 'inline-block'}),

        html.Div([
            html.Div([
                dcc.RadioItems(
                    id='data_selector',
                    options=[
                        {'label': 'Live Data', 'value': 'live'},
                        {'label': 'Historic Data', 'value': 'past'}
                    ],
                    value='live',  # Default value
                    labelStyle={'display': 'inline-block'},
                    style={'font-family': 'Arial, sans-serif'}
                ),

                # Live Data Input Field
                html.Div([
                    html.Label("Time Window (hours):", style={'font-family': 'Arial, sans-serif'}),
                    dcc.Input(id='live_time_window_input', type='number', placeholder='Enter Time Window', value=3)
                ], style={'padding': '10px 0'}),

                # Past Data Input Fields
                html.Div([
                    html.Label("Start DateTime (YYYY-MM-DD HH:MM):", style={'font-family': 'Arial, sans-serif'}),
                    dcc.Input(id='past_start_datetime', type='text', placeholder='2023-11-18 05:00',
                              style={'margin-right': '10px'}, value='2023-11-18 05:00'),
                    html.Label("End DateTime (YYYY-MM-DD HH:MM):", style={'font-family': 'Arial, sans-serif'}),
                    dcc.Input(id='past_end_datetime', type='text', placeholder='2023-11-18 09:00', value='2023-11-18 09:00')
                ], style={'padding': '10px 0'})

            ], style={'display': 'inline-block'}),
        ],)

    ], style={'margin': '0'}),

    html.Div([
        dcc.Graph(id='nmr_plot', style={'margin': '0'}),
    ], style={'width': '100%', 'margin': '0 auto'}),

    html.Div([
        html.H2("First and Last NMR Spectra", style={'font-family': 'Arial, sans-serif'}),
        dcc.Graph(id='first_last_spectrum_plot', style={'margin': '0'}),
    ], style={'width': '100%', 'margin': '0 auto'}),

    html.Div(id='dummy_div')
], style={'max-width': '90%', 'margin': '0 auto'})
