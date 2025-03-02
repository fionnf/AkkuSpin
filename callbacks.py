from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import dcc
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import data_processing
import utils
import os
import eclabfiles as ecf
import pandas as pd
import nmrglue as ng
from datetime import datetime, timedelta
import plotting
import dash
from dash import callback_context
from tqdm import tqdm

def register_callbacks(app):
    @app.callback(
        [Output('nmr_plot', 'figure'),
         Output('first_last_spectrum_plot', 'figure'),
         Output('fid_plot', 'figure'),
         Output('cycle_plot', 'figure'),
         Output('message_area', 'children'),],
        [State('dummy_div', 'children'),
         State('nmr_folder_input', 'value'),
         State('voltage_folder_input', 'value'),
         State('ppm_min_input', 'value'),
         State('ppm_max_input', 'value'),
         State('nmr_format_selector', 'value'),
         State('nucleus_selector','value'),
         State('data_selector', 'value'),
         State('live_time_window_input', 'value'),
         State('past_start_datetime', 'value'),
         State('past_end_datetime','value')],
         [Input('update_button', 'n_clicks'),
         Input('interval-component', 'n_intervals')
         ],
    )

    def update_plots(_, nmr_folder, voltage_folder, ppm_min, ppm_max, format_type,
                     nucleus, data_selector, live_time_window, past_start_datetime, past_end_datetime, n_clicks, n_intervals):
        ctx = callback_context

        # Identify what triggered the callback
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if not all([nmr_folder, voltage_folder, ppm_min, ppm_max, format_type, nucleus, data_selector, live_time_window,
                    past_start_datetime, past_end_datetime]):
            error_message = "Incomplete or invalid input. Please check your inputs."
            return go.Figure(), go.Figure(), go.Figure(), error_message

        if ppm_min > ppm_max:
            error_message = "ppm min > ppm max, Choose a valid ppm range"
            return go.Figure(), go.Figure(), go.Figure(), error_message

        try:
            if trigger_id == 'update_button' or trigger_id == 'interval-component':
                ppm_min, ppm_max = float(ppm_min), float(ppm_max)

                if data_selector == 'live':
                    end_datetime = utils.get_most_recent_time(nmr_folder)
                    if end_datetime is None:
                        raise ValueError("No NMR spectra found in the specified folder, or incorrect spectra naming (eg. 1H_20231101T000823.fid).")
                    start_datetime = end_datetime - utils.datetime.timedelta(hours=float(live_time_window))
                elif data_selector == 'past':
                    # Calculate past time range based on user input
                    start_datetime = datetime.strptime(past_start_datetime, '%Y-%m-%d %H:%M')
                    end_datetime = datetime.strptime(past_end_datetime, '%Y-%m-%d %H:%M')
                elif data_selector != 'live' and data_selector != 'past':
                    raise ValueError('dataselector: ', data_selector)


                # Find NMR spectra in the calculated time range
                spectra_paths = data_processing.find_spectra_in_range(nmr_folder, start_datetime, end_datetime, nucleus)
                spectra_paths = sorted(spectra_paths)
                print(f'finding nmr spectra in time range: {start_datetime},{end_datetime}')
                # Extract times for the first and last NMR spectra
                nmr_times = [data_processing.extract_date_time(path) for path in spectra_paths]
                nmr_start_time, nmr_end_time = min(nmr_times), max(nmr_times)

                print('Plotting voltage trace')
                eclab_df = data_processing.process_eclab(voltage_folder)
                ec_v_df = eclab_df[1]
                volt_df = data_processing.eclab_voltage(ec_v_df, start_datetime, end_datetime)
                print("Columns in volt_df:", volt_df.columns)
                print("First few rows of volt_df:", volt_df.head())

                autophase_done = False
                phase_params = (None, None)

                heatmap_intensity = []
                spectrum_runtime = []
                ppm_values = None
                progress_bar = tqdm(total=len(spectra_paths), desc="Processing Spectra")
                for index, path in enumerate(spectra_paths):
                    # Ensure correct argument passing. Adjust according to the updated function signature
                    if not autophase_done:
                        # For the first spectrum, apply autophasing
                        dic, data, p0, p1, runtime, obs, sw, car = data_processing.process_nmr_data(
                            path=path,
                            nmr_format=format_type,
                            apply_autophase=False,
                            #apply_autophase=True,
                            #p0=0,
                            #p1=0,
                            #custom phasing parameters below override autophase...
                            p0=-260.143324985434,
                            p1=26.94935982565039
                        )
                        # Store phase parameters from the first spectrum for subsequent use
                        phase_params = (p0, p1)
                        autophase_done = True
                    else:
                        # For subsequent spectra, use stored phase parameters without autophasing
                         dic, data, p0, p1, runtime, obs, sw, car = data_processing.process_nmr_data(
                            path=path,
                            nmr_format=format_type,
                            apply_autophase=False,
                            p0=phase_params[0],
                            p1=phase_params[1]
                        )

                    spectrum_runtime.append(runtime)

                    if ppm_values is None:
                        uc = ng.pipe.make_uc(dic, data)
                        ppm_values = uc.ppm_scale()

                    intensity = data.real
                    heatmap_intensity.append(intensity)
                    progress_bar.update(1)
                progress_bar.close()

                # Find the indices for the desired ppm range
                ppm_indices = [i for i, ppm in enumerate(ppm_values) if ppm_min <= ppm <= ppm_max]

                # Filter the ppm values and intensities according to the indices
                filtered_ppm_values = [ppm_values[i] for i in ppm_indices]
                filtered_heatmap_intensity = [[intensity[i] for i in ppm_indices] for intensity in heatmap_intensity]
                filtered_ppm_values = list(filtered_ppm_values)

                # Create a subplot figure with 2 columns
                fig = make_subplots(rows=1, cols=2, shared_yaxes=True, column_widths=[0.67, 0.33], horizontal_spacing=0.02)

                # Get the true start time (timestamp of the first spectrum in the folder)
                true_start_time = utils.find_true_start_time(nmr_folder, nucleus)
                experiment_start_time = true_start_time
                print("Creating NMR Heatmap")
                fig_nmr_heatmap = plotting.create_nmr_heatmap(filtered_ppm_values, nmr_times, filtered_heatmap_intensity, experiment_start_time)
                # Pass the start time to the voltage trace function
                fig_voltage_trace = plotting.create_voltage_trace(volt_df, experiment_start_time)

                fig.add_trace(fig_nmr_heatmap['data'][0], row=1, col=1)
                fig.add_trace(fig_voltage_trace['data'][0], row=1, col=2)
                fig.add_trace(fig_voltage_trace['data'][1], row=1, col=2)

                fig.update_layout(
                    height=800,
                    width=1200,
                )

                # Add annotation in the bottom-right corner
                fig.add_annotation(
                    text="Akkuspin",  # Text to display
                    font=dict(size=12, color="lightgrey"),  # Font size and color
                    xref="paper",  # Reference the full figure width
                    yref="paper",  # Reference the full figure height
                    x=0.62,  # Bottom-right corner (95% of the width)
                    y=0.01,  # Bottom edge (5% of the height)
                    showarrow=False  # No arrow
                )

                fig.update_xaxes(
                    range=[ppm_max, ppm_min],
                    title_text="Chemical Shift (ppm)",
                    title_font=dict(size=20, color="black"),
                    tickfont=dict(size=18, color="black"),
                    row=1,
                    col=1
                )

                fig.update_yaxes(
                    title_text="Experiment Time (h)",
                    title_font=dict(size=20, color="black"),
                    tickfont=dict(size=18, color="black"),
                    row=1,
                    col=1
                )

                fig.update_xaxes(
                    title_text="Voltage Profile (V)",
                    title_font=dict(size=20, color="black"),
                    tickfont=dict(size=18, color="black"),
                    row=1,
                    col=2
                )

                first_spectrum_path, last_spectrum_path = utils.find_first_last_spectra(nmr_folder, nucleus)

                spectra_fig = plotting.create_spectra_fig(first_spectrum_path, last_spectrum_path, format_type, nmr_start_time, nmr_end_time)

                fid_fig = plotting.create_3d_fid_plot(last_spectrum_path, format_type)

                # Check if electrochemistry data directory is provided
                if voltage_folder:
                    try:
                        # Generate electrochemical plot
                        cycle_plot = plotting.plot_capacities_and_efficiency_eclab(voltage_folder)
                    except Exception as e:
                        print(f"Error processing data or generating battery cycling plot: {e}")
                        cycle_plot = go.Figure()
                else:
                    cycle_plot = go.Figure()

                return fig, spectra_fig, fid_fig, cycle_plot, ""
            else:
                print("Callback triggered by an unexpected source.")
                return go.Figure(), go.Figure(), go.Figure(), go.Figure(), ""

        except Exception as e:
            print(f"Error in heatmap callback: {e}")
            return go.Figure(), go.Figure(), go.Figure(), go.Figure(), ""



def register_integration_callback(app):
    @app.callback(
        Output('int-plot', 'figure'),
        [
            Input('integrate-button', 'n_clicks')
        ],
        [
            State('ppm-range-min', 'value'),
            State('ppm-range-max', 'value'),
            State('internal-ppm-range-min', 'value'),
            State('internal-ppm-range-max', 'value'),
            State('normalize-standard-to', 'value'),
            State('voltage-filter-type', 'value'),
            State('voltage-filter-value', 'value'),
            State('nmr_folder_input', 'value'),
            State('voltage_folder_input', 'value'),
            State('data_int', 'value'),
            State('int_start_datetime', 'value'),
            State('int_end_datetime', 'value')
        ]
    )
    def integrate_spectra(n_clicks, ppm_min, ppm_max, internal_ppm_min, internal_ppm_max, normalize_to,
                          voltage_filter_type, voltage_filter_value, nmr_folder, voltage_folder,data_int,
                          int_start_datetime, int_end_datetime):
        if n_clicks is None:
            raise PreventUpdate

        # Check if inputs are valid
        if not all([ppm_min, ppm_max, internal_ppm_min, internal_ppm_max, normalize_to, voltage_filter_type, voltage_filter_value, nmr_folder, voltage_folder,data_int,
                          int_start_datetime, int_end_datetime]):
            return go.Figure()

        print("Integration Inputs valid")

        # Read integration limits
        integration_limits = [
            ("anolyte", ppm_min, ppm_max),
            ("internal_standard", internal_ppm_min, internal_ppm_max)
        ]

        # Load voltage data
        eclab_df = data_processing.process_eclab(voltage_folder)
        ec_v_df = eclab_df[1]
        voltages = ec_v_df['Voltage']

        # Filter voltage data based on the specified criteria
        if voltage_filter_type == 'gt':
            filtered_voltages = ec_v_df[ec_v_df['Voltage'] > voltage_filter_value]
        else:
            filtered_voltages = ec_v_df[ec_v_df['Voltage'] < voltage_filter_value]

        valid_times = filtered_voltages['Timestamp']

        # Load and process NMR spectra
        spectra_paths = sorted(data_processing.find_spectra_in_range(nmr_folder, datetime.min, datetime.max, '19F'))  # Adjust the nucleus parameter as needed
        integrated_values = []
        times = []


        # Convert NMR spectrum times to pandas datetime for easier matching
        nmr_times = pd.Series([data_processing.extract_date_time(path) for path in spectra_paths])
        if data_int == 'range':
            start_datetime = pd.to_datetime(int_start_datetime)
            end_datetime = pd.to_datetime(int_end_datetime)
            nmr_times = nmr_times[(nmr_times >= start_datetime) & (nmr_times <= end_datetime)]

        # Extract start and end times of NMR spectra
        nmr_start_time = nmr_times.min()
        nmr_end_time = nmr_times.max()

        # Filter voltage data based on the common time range
        filtered_voltages = filtered_voltages[(filtered_voltages['Timestamp'] >= nmr_start_time) & (filtered_voltages['Timestamp'] <= nmr_end_time)]

        def round_to_nearest_minute(timestamp):
            return timestamp.replace(second=0, microsecond=0)

        valid_times = filtered_voltages['Timestamp']
        valid_times_rounded = [round_to_nearest_minute(time) for time in valid_times]
        valid_times_filtered = []
        for time in valid_times_rounded:
            if time not in valid_times_filtered:
                valid_times_filtered.append(time)
        valid_times = valid_times_filtered

        # Initialize progress bar
        progress_bar = tqdm(total=len(valid_times), desc="Integration Progress")

        for voltage_time in valid_times:
            # Find the closest NMR time
            closest_nmr_time = nmr_times.iloc[(nmr_times - voltage_time).abs().argsort()[:1]].values[0]
            spectrum_path = spectra_paths[nmr_times[nmr_times == closest_nmr_time].index[0]]
            results = data_processing.integrate_spectrum(spectrum_path, integration_limits)
            internal_standard_area = None
            integrated_area = None
            for name, start, stop, area in results:
                if name == "internal_standard":
                    internal_standard_area = area
                else:
                    integrated_area = area
                # Calculate normalized value if both areas are obtained
            normalized_value = integrated_area#/internal_standard_area
            integrated_values.append(normalized_value)
            times.append(closest_nmr_time)
            progress_bar.update(1)
        progress_bar.close()
        # Convert numpy datetime64 objects to Python datetime objects
        times = [ts.astype('M8[ms]').astype('O') for ts in times]

        # Create the plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=integrated_values, mode='markers', name='Integrated peak'))
        # Adding a line trace
        # fig.add_trace(go.Scatter(x=times, y=integrated_values, mode='lines', name='Integrated peak (line)'))
        # Display the plot
        fig.update_layout(
            title='Integrated NMR Spectra',
            xaxis_title='Timestamp',
            yaxis_title='Integrated Area',
            xaxis=dict(
                type='date'  # Set x-axis type to date
            )
        )
        text_content = utils.generate_text_content(integrated_values, times)
        print("------------- INTEGRALS TEXT -------------")
        print("Minimum PPM:", ppm_min)
        print("Maximum PPM:", ppm_max)
        print(text_content)
        print("------------- INTEGRALS List -------------")
        print(integrated_values)
        print(times)
        print("------------------------------------------")

        return fig