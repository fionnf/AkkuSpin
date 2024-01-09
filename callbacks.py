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
         Output('first_last_spectrum_plot', 'figure')],
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

        try:
            if trigger_id == 'update_button' or trigger_id == 'interval-component':
                ppm_min, ppm_max = float(ppm_min), float(ppm_max)

                if data_selector == 'live':
                    # Calculate time range based on user input
                    end_datetime = utils.get_most_recent_time(nmr_folder)
                    if end_datetime is None:
                        raise ValueError("No NMR spectra found in the specified folder.")
                    start_datetime = end_datetime - utils.datetime.timedelta(hours=float(live_time_window))
                elif data_selector == 'past':
                    # Calculate past time range based on user input
                    start_datetime = datetime.strptime(past_start_datetime, '%Y-%m-%d %H:%M')
                    end_datetime = datetime.strptime(past_end_datetime, '%Y-%m-%d %H:%M')
                elif data_selector != 'live' and data_selector != 'past':
                    print('dataselector error: ', data_selector)

                # Find NMR spectra in the calculated time range
                spectra_paths = data_processing.find_spectra_in_range(nmr_folder, start_datetime, end_datetime, nucleus)

                # Extract times for the first and last NMR spectra
                nmr_times = [data_processing.extract_date_time(path) for path in spectra_paths]
                nmr_start_time, nmr_end_time = min(nmr_times), max(nmr_times)

                volt_df = data_processing.process_eclab_files(voltage_folder, nmr_start_time, nmr_end_time)

                autophase_done = False
                phase_params = (None, None)

                heatmap_intensity = []
                ppm_values = None

                for path in spectra_paths:
                    dic, data, sw, obs, car, label = data_processing.read_nmr_data_lowmem(path, format_type)

                    if not autophase_done:
                        # Perform autophasing for the first spectrum
                        dic, data, p0, p1 = data_processing.process_nmr_data(dic, data, sw, obs, car, format_type, apply_autophase=True)
                        phase_params = (p0, p1)
                        autophase_done = True
                    else:
                        # Apply the stored phase parameters for subsequent spectra
                        dic, data, _, _ = data_processing.process_nmr_data(dic, data, sw, obs, car, format_type, p0=phase_params[0], p1=phase_params[1],
                                                           apply_autophase=False)

                    uc = ng.pipe.make_uc(dic, data)
                    if ppm_values is None:
                        ppm_values = uc.ppm_scale()  # Get ppm scale from the first spectrum

                    intensity = data.real  # Assuming you want to plot the real part
                    heatmap_intensity.append(intensity)

                # Reduce the resolution for testing
                # reduced_ppm_values = ppm_values[::10]  # Take every 1000th value as a sample
                # reduced_heatmap_intensity = [intensity[::10] for intensity in heatmap_intensity]

                # Find the indices for the desired ppm range
                ppm_indices = [i for i, ppm in enumerate(ppm_values) if ppm_min <= ppm <= ppm_max]

                # Filter the ppm values and intensities according to the indices
                filtered_ppm_values = [ppm_values[i] for i in ppm_indices]
                filtered_heatmap_intensity = [[intensity[i] for i in ppm_indices] for intensity in heatmap_intensity]

                # Create a subplot figure with 2 columns
                fig = make_subplots(rows=1, cols=2, shared_yaxes=True, column_widths=[0.75, 0.25], horizontal_spacing=0.02)

                fig_nmr_heatmap = plotting.create_nmr_heatmap(filtered_ppm_values, nmr_times, filtered_heatmap_intensity)
                fig_voltage_trace = plotting.create_voltage_trace(volt_df)

                fig.add_trace(fig_nmr_heatmap['data'][0], row=1, col=1)
                fig.add_trace(fig_voltage_trace['data'][0], row=1, col=2)

                first_spectrum_path, last_spectrum_path = utils.find_first_last_spectra(nmr_folder, nucleus)

                spectra_fig = plotting.create_spectra_fig(first_spectrum_path, last_spectrum_path, format_type, nmr_start_time, nmr_end_time)

                return fig, spectra_fig
            else:
                # If the callback wasn't triggered by the button or the interval, you can decide what to do
                # For example, you might want to return the current figures without updating
                print("Callback triggered by an unexpected source.")
                return go.Figure(), go.Figure()

        except Exception as e:
            print(f"Error: {e}")
            return go.Figure(), go.Figure()
