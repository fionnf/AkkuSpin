from dash import html, dcc
import dash_bootstrap_components as dbc

cyclerfolder = '/Users/fionnferreira/Downloads/BioLogic Files/flow_nmr'
NMR_folder = '/Users/fionnferreira/Downloads/NMR'

def integration_layout(sans_serif_font, input_style):
    radio_size = '16px'
    return html.Div([
        html.Div([
            html.H2("Integration Settings", style={'font-family': sans_serif_font, 'font-size': '18px', 'line-height': '1.5', 'padding': '10px', 'margin-top': '0'}),
        ], style={ 'margin': '0', 'padding': '0'}),

        dbc.Row([
            dbc.Col([
                html.Label('PPM Range of Sample to Integrate', style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='ppm-range-min', type='number', placeholder='Min', step=0.0001, style=input_style, value='-58.7'),
                dcc.Input(id='ppm-range-max', type='number', placeholder='Max', step=0.0001, style=input_style, value='-58.6'),
            ], width=4),
            dbc.Col([
                html.Label('PPM Range of Internal Standard', style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='internal-ppm-range-min', type='number', placeholder='Min', step=0.0001, style=input_style, value='-115'),
                dcc.Input(id='internal-ppm-range-max', type='number', placeholder='Max', step=0.0001, style=input_style, value='-113'),
            ], width=4),
            dbc.Col([
                dcc.RadioItems(
                    id='data_int',
                    options=[
                        {'label': 'Plot all Data', 'value': 'all'},
                        {'label': 'Plot time range', 'value': 'range'}
                    ],
                    value='range',
                    labelStyle={'display': 'block'},
                    style={'font-family': sans_serif_font, 'font-size': radio_size}
                ),
                html.Label("Integration Start DateTime (YYYY-MM-DD HH:MM):", style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='int_start_datetime', type='text', placeholder='2023-11-14 17:56', style=input_style, value='2024-04-22 13:00'),
                html.Label("Integration End DateTime (YYYY-MM-DD HH:MM):", style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='int_end_datetime', type='text', placeholder='2023-11-15 01:06', value='2024-04-22 20:00', style=input_style),
            ], width=4)
        ]),
        dbc.Row([
            dbc.Col([
                html.Label('Normalize Standard To', style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='normalize-standard-to', type='number', placeholder='Number', step=0.01, style=input_style, value='1'),
            ], width=4),
            dbc.Col([
                html.Label('Voltage Filter', style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.RadioItems(
                    id='voltage-filter-type',
                    options=[
                        {'label': '>', 'value': 'gt'},
                        {'label': '<', 'value': 'lt'}
                    ],
                    value='gt',
                    labelStyle={'display': 'inline-block', 'margin-right': '10px', 'font-family': sans_serif_font, 'font-size': '16px'},
                    style={'margin-bottom': '10px'}
                ),
                dcc.Input(id='voltage-filter-value', type='number', placeholder='Value', step=0.0001, style=input_style),
            ], width=4)
        ]),
        dbc.Row([
            dbc.Col([
                html.Button('Integrate', id='integrate-button', n_clicks=0, style={'font-family': sans_serif_font, 'font-size': '16px', 'padding': '5px 10px'}),
            ], width=12)
        ], style={'margin-top': '10px'}),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='int-plot')
            ], width=12)
        ])
    ], style={'max-width': '90%', 'margin': '0 auto', 'background-color': '#f7f7f7', 'box-sizing': 'border-box'})

def create_layout():
    sans_serif_font = 'Arial, sans-serif'
    radio_size = '16px'

    input_style = {
        'width': '97%',
        'height': '1.2em',  # Set to text height
        'font-family': sans_serif_font,  # Sans-serif font
        'border': '1px solid #ccc',
        'color': 'black',
        'background-color': '#f7f7f7',
        'padding': '5px',
        'margin-bottom': '10px'
    }

    config = {
        "toImageButtonOptions": {
            "format": "png",  # Options: 'png', 'svg', 'jpeg', 'webp'
            "filename": "Akkuspin Heatmap",  # Default file name
            "height": 800,
            "width": 1200,
            "scale": 3
        }
    }

    return html.Div([
        html.Div([
            html.H1("AkkuSpin", style={'text-align': 'center', 'padding': '20px 0', 'color': 'white', 'font-family': sans_serif_font}),
        ], style={'background-color': '#0047AB', 'color': 'white', 'margin': '0', 'padding': '0'}),

        # Interval component for live updates
        dcc.Interval(
            id='interval-component',
            interval=900 * 1000,  # in milliseconds
            n_intervals=0
        ),

        html.Div([
            # Global Settings
            html.Div([
                html.H2("Global Settings", style={'font-family': sans_serif_font, 'font-size': '18px', 'line-height': '1.5', 'padding': '10px', 'margin-top': '0'}),
                html.Label("NMR Folder Path:", style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='nmr_folder_input', type='text', placeholder='Enter NMR Folder Path',
                          value=NMR_folder, style=input_style),
                html.Label("Voltage Folder Path:", style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='voltage_folder_input', type='text', placeholder='Enter Voltage Folder Path',
                          value=cyclerfolder, style=input_style),
                html.Label("NMR Format:", style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.RadioItems(
                    id='nmr_format_selector',
                    options=[
                        {'label': 'Bruker', 'value': 'Bruker'},
                        {'label': 'Varian', 'value': 'Varian'}
                    ],
                    value='Varian',
                    labelStyle={'display': 'block'},
                    style={'font-family': sans_serif_font, 'font-size': radio_size}
                ),
                html.Label("Nucleus:", style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.RadioItems(
                    id='nucleus_selector',
                    options=[
                        {'label': '1H', 'value': '1H'},
                        {'label': '19F', 'value': '19F'}
                    ],
                    value='19F',
                    labelStyle={'display': 'block'},
                    style={'font-family': sans_serif_font, 'font-size': radio_size}
                ),
            ], style={'width': '32%', 'background-color': '#f7f7f7', 'padding': '20px', 'box-sizing': 'border-box',
                      'margin-right': '2%'}),

            # Update Settings
            html.Div([
                html.H2("Update Settings", style={'font-family': sans_serif_font, 'font-size': '18px', 'line-height': '1.5', 'padding': '10px', 'margin-top': '0'}),
                dcc.RadioItems(
                    id='data_selector',
                    options=[
                        {'label': 'Live Data', 'value': 'live'},
                        {'label': 'Historic Data', 'value': 'past'}
                    ],
                    value='live',
                    labelStyle={'display': 'block'},
                    style={'font-family': sans_serif_font, 'font-size': radio_size}
                ),
                html.Label("Live Time Window (hours):", style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='live_time_window_input', type='number', placeholder='Enter Time Window', value=3,
                          style=input_style),
                html.Label("Historic Start DateTime (YYYY-MM-DD HH:MM):", style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='past_start_datetime', type='text', placeholder='2024-12-13 12:50',
                          style=input_style, value='2024-12-13 12:50'),
                html.Label("Historic End DateTime (YYYY-MM-DD HH:MM):", style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='past_end_datetime', type='text', placeholder='2024-12-14 01:50',
                          value='2024-12-14 01:50', style=input_style),
            ], style={'width': '32%', 'background-color': '#f7f7f7', 'padding': '20px', 'box-sizing': 'border-box',
                      'margin-right': '2%'}),

            # Plot Settings
            html.Div([
                html.H2("Plot Settings", style={'font-family': sans_serif_font, 'font-size': '18px', 'line-height': '1.5', 'padding': '10px', 'margin-top': '0'}),
                html.Label("Min PPM:", style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='ppm_min_input', type='number', placeholder='Min PPM', value=-61,
                          style=input_style),
                html.Label("Max PPM:", style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='ppm_max_input', type='number', placeholder='Max PPM', value=-57.5,
                          style=input_style),
                html.Button('Update', id='update_button', n_clicks=0),
            ], style={'width': '32%', 'background-color': '#f7f7f7', 'padding': '20px', 'box-sizing': 'border-box'}),
        ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '20px'}),

        #Message area
        html.Div(
            id='message_area',
            style={'font-family': sans_serif_font, 'font-size': '16px'}
        ),

        # Progress bar (added here)
        dbc.Progress(id='progress-bar', value=0, striped=True, animated=True, style={'margin': '10px 0'}),

        # NMR Plot
        html.Div([
            dcc.Graph(id='nmr_plot', style={'margin': '0'}, config=config),
        ], style={'width': '100%', 'margin': '0 auto'}),

        # First and Last NMR Spectra Plot
        html.Div([
            html.H2("First and Last NMR Spectra", style={'font-family': sans_serif_font, 'font-size': '18px', 'line-height': '1.5', 'padding': '10px', 'margin-top': '0'}),
            dcc.Graph(id='first_last_spectrum_plot', style={'margin': '0'}, config=config),
        ], style={'width': '100%', 'margin': '0 auto'}),

        # Cycling data plot
        html.Div([
            html.H2("Battery Cycling Data",
                    style={'font-family': sans_serif_font, 'font-size': '18px', 'line-height': '1.5', 'padding': '10px',
                           'margin-top': '0'}),
            dcc.Graph(id='cycle_plot', style={'margin': '0'}, config=config),
        ], style={'width': '100%', 'margin': '0 auto'}),

        # FID Plot
        html.Div([
            html.H2("FID", style={'font-family': sans_serif_font, 'font-size': '18px', 'line-height': '1.5', 'padding': '10px',
                           'margin-top': '0'}),
            dcc.Graph(id='fid_plot', style={'margin': '0'}, config=config),
        ], style={'width': '100%', 'margin': '0 auto'}),

        # Integration layout
        integration_layout(sans_serif_font, input_style),

        # Store component to save input states
        dcc.Store(id='input-storage', storage_type='local'),

        html.Div(id='dummy_div')
    ], style={'max-width': '90%', 'margin': '0 auto'})
