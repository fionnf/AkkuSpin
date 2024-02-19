from dash import html, dcc

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
        'toImageButtonOptions': {
            'format': 'svg',
            'filename': 'nmr_heatmap',
            'height': 500,
            'width': 700,
            'scale': 1
        }
    }

    return html.Div([
        html.Div([
            html.H1("AkkuSpin", style={'text-align': 'center', 'padding': '20px 0', 'color': 'white', 'font-family': sans_serif_font}),
        ], style={'background-color': '#0047AB', 'color': 'white', 'margin': '0', 'padding': '0'}),

        # Interval component for live updates
        dcc.Interval(
            id='interval-component',
            interval=500 * 1000,  # in milliseconds
            n_intervals=0
        ),

        html.Div([
            # Global Settings
            html.Div([
                html.H2("Global Settings", style={'font-family': sans_serif_font, 'font-size': '18px', 'line-height': '1.5', 'padding': '10px', 'margin-top': '0'}),
                html.Label("NMR Folder Path:", style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='nmr_folder_input', type='text', placeholder='Enter NMR Folder Path',
                          value=r'Test\NMR Folder', style=input_style),
                html.Label("Voltage Folder Path:", style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='voltage_folder_input', type='text', placeholder='Enter Voltage Folder Path',
                          value=r'Test\Cyclerfolder', style=input_style),
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
                dcc.Input(id='past_start_datetime', type='text', placeholder='2023-11-18 05:00',
                          style=input_style, value='2023-11-18 05:00'),
                html.Label("Historic End DateTime (YYYY-MM-DD HH:MM):", style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='past_end_datetime', type='text', placeholder='2023-11-18 09:00',
                          value='2023-11-18 09:00', style=input_style),
            ], style={'width': '32%', 'background-color': '#f7f7f7', 'padding': '20px', 'box-sizing': 'border-box',
                      'margin-right': '2%'}),

            # Plot Settings
            html.Div([
                html.H2("Plot Settings", style={'font-family': sans_serif_font, 'font-size': '18px', 'line-height': '1.5', 'padding': '10px', 'margin-top': '0'}),
                html.Label("Min PPM:", style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='ppm_min_input', type='number', placeholder='Min PPM', value=-58.75,
                          style=input_style),
                html.Label("Max PPM:", style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='ppm_max_input', type='number', placeholder='Max PPM', value=-57.25,
                          style=input_style),
                html.Label("Theoretical Capacity(mAh)", style={'font-family': sans_serif_font, 'font-size': '16px'}),
                dcc.Input(id='theoretical_capacity', type='number', placeholder='Enter theoretical capacity', value=0.8,
                          style=input_style),
                html.Button('Update', id='update_button', n_clicks=0),
            ], style={'width': '32%', 'background-color': '#f7f7f7', 'padding': '20px', 'box-sizing': 'border-box'}),
        ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '20px'}),

        #Message area
        html.Div(
            id='message_area',
            style={'font-family': sans_serif_font, 'font-size': '16px'}
        ),

        # NMR Plot
        html.Div([
            dcc.Graph(id='nmr_plot', style={'margin': '0'}, config=config),
        ], style={'width': '100%', 'margin': '0 auto'}),

        # First and Last NMR Spectra Plot
        html.Div([
            html.H2("First and Last NMR Spectra", style={'font-family': sans_serif_font, 'font-size': '18px', 'line-height': '1.5', 'padding': '10px', 'margin-top': '0'}),
            dcc.Graph(id='first_last_spectrum_plot', style={'margin': '0'}, config=config),
        ], style={'width': '100%', 'margin': '0 auto'}),

        # First and Last NMR Spectra Plot
        html.Div([
            html.H2("FID", style={'font-family': sans_serif_font, 'font-size': '18px', 'line-height': '1.5', 'padding': '10px',
                           'margin-top': '0'}),
            dcc.Graph(id='fid_plot', style={'margin': '0'}, config=config),
        ], style={'width': '100%', 'margin': '0 auto'}),

        # Cycling data plot
        html.Div([
            html.H2("Battery Cycling Data",
                    style={'font-family': sans_serif_font, 'font-size': '18px', 'line-height': '1.5', 'padding': '10px',
                           'margin-top': '0'}),
            dcc.Graph(id='cycle_plot', style={'margin': '0'}, config=config),
        ], style={'width': '100%', 'margin': '0 auto'}),

        html.Div(id='dummy_div')
    ], style={'max-width': '90%', 'margin': '0 auto'})
