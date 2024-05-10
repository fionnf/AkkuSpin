from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import data_processing
import utils
import os
import eclabfiles as ecf
import pandas as pd
import nmrglue as ng
from datetime import datetime
import plotting
import dash
from dash import callback_context

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
                print(f'finding nmr spectra in time range: {start_datetime},{end_datetime}')
                # Extract times for the first and last NMR spectra
                nmr_times = [data_processing.extract_date_time(path) for path in spectra_paths]
                nmr_start_time, nmr_end_time = min(nmr_times), max(nmr_times)

                print('Plotting voltage trace')
                eclab_df = data_processing.process_eclab(voltage_folder)
                ec_v_df = eclab_df[1]
                volt_df = data_processing.eclab_voltage(ec_v_df, start_datetime, end_datetime)

                autophase_done = False
                phase_params = (None, None)

                heatmap_intensity = []
                spectrum_runtime = []
                ppm_values = None

                for index, path in enumerate(spectra_paths):
                    # Ensure correct argument passing. Adjust according to the updated function signature
                    if not autophase_done:
                        # For the first spectrum, apply autophasing
                        dic, data, p0, p1, runtime, obs, sw, car = data_processing.process_nmr_data(
                            path=path,
                            nmr_format=format_type,
                            apply_autophase=True,
                            p0=0,
                            p1=0
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

                # Reduce the resolution for larger widths
                if ppm_max - ppm_min > 25:
                    reduction_factor = 10
                    # Apply resolution reduction
                    print('Applying resolution reduction')
                    ppm_values = ppm_values[::reduction_factor]
                    heatmap_intensity = [intensity[::reduction_factor] for intensity in heatmap_intensity]

                # Find the indices for the desired ppm range
                ppm_indices = [i for i, ppm in enumerate(ppm_values) if ppm_min <= ppm <= ppm_max]

                # Filter the ppm values and intensities according to the indices
                filtered_ppm_values = [ppm_values[i] for i in ppm_indices]
                filtered_heatmap_intensity = [[intensity[i] for i in ppm_indices] for intensity in heatmap_intensity]
                filtered_ppm_values = list(reversed(filtered_ppm_values))

                # Create a subplot figure with 2 columns
                fig = make_subplots(rows=1, cols=2, shared_yaxes=True, column_widths=[0.75, 0.25], horizontal_spacing=0.02)

                fig_nmr_heatmap = plotting.create_nmr_heatmap(filtered_ppm_values, spectrum_runtime, filtered_heatmap_intensity)
                fig_voltage_trace = plotting.create_voltage_trace(volt_df)

                fig.add_trace(fig_nmr_heatmap['data'][0], row=1, col=1)
                fig.add_trace(fig_voltage_trace['data'][0], row=1, col=2)

                fig.update_xaxes(range=[ppm_max, ppm_min], title_text="Chemical Shift (ppm)", row=1, col=1)

                fig.update_yaxes(title_text="Time", row=1, col=1)
                fig.update_xaxes(title_text="Voltage", row=1, col=2)

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
