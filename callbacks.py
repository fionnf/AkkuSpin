from dash.dependencies import Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import data_processing
import utils

def register_callbacks(app):
    @app.callback(
        [Output('nmr_plot', 'figure'),
         Output('first_last_spectrum_plot', 'figure')],
        [Input('dummy_div', 'children'),
         Input('nmr_folder_input', 'value'),
         Input('voltage_folder_input', 'value'),
         Input('ppm_min_input', 'value'),
         Input('ppm_max_input', 'value'),
         Input('time_window_input', 'value')]
    )
    def update_plots(_, nmr_folder, voltage_folder, ppm_min, ppm_max, time_window_hours):
        print("Callback triggered")
        try:
            print("try")
            # Parse ppm_min and ppm_max as float values
            ppm_min, ppm_max = float(ppm_min), float(ppm_max)

            # Calculate time range based on user input
            most_recent_time = get_most_recent_time(nmr_folder)
            if most_recent_time is None:
                raise ValueError("No NMR spectra found in the specified folder.")
            start_date = most_recent_time - datetime.timedelta(hours=float(time_window_hours))

            # Find NMR spectra in the calculated time range
            spectra_paths = find_spectra_in_range(nmr_folder, start_date, most_recent_time, '19F')

            # Extract times for the first and last NMR spectra
            nmr_times = [extract_date_time(path) for path in spectra_paths]
            nmr_start_time, nmr_end_time = min(nmr_times), max(nmr_times)

            # Identify the MPR and MPL file in the voltage_folder
            mpr_file = None
            mpl_file = None
            for file in os.listdir(voltage_folder):
                if file.endswith('.mpr'):
                    mpr_file = os.path.join(voltage_folder, file)
                elif file.endswith('.mpl'):
                    mpl_file = os.path.join(voltage_folder, file)

            if not mpr_file or not mpl_file:
                raise FileNotFoundError("MPR or MPL file not found in the provided folder.")

            # Parse the MPR file into a DataFrame for voltage data
            df = ecf.to_df(mpr_file)
            start_time = extract_start_time(mpl_file)
            df['absolute_time'] = pd.to_timedelta(df['time'], unit='s') + start_time
            filtered_df = df[(df['absolute_time'] >= nmr_start_time) & (df['absolute_time'] <= nmr_end_time)]

            autophase_done = False
            phase_params = (None, None)

            heatmap_intensity = []
            ppm_values = None

            for path in spectra_paths:
                dic, data, sw, obs, car, label = read_varian_lowmem(path)

                if not autophase_done:
                    # Perform autophasing for the first spectrum
                    dic, data, p0, p1 = process_nmr_data(dic, data, sw, obs, car, apply_autophase=True)
                    phase_params = (p0, p1)
                    autophase_done = True
                else:
                    # Apply the stored phase parameters for subsequent spectra
                    dic, data, _, _ = process_nmr_data(dic, data, sw, obs, car, p0=phase_params[0], p1=phase_params[1],
                                                       apply_autophase=False)

                uc = ng.pipe.make_uc(dic, data)
                if ppm_values is None:
                    ppm_values = uc.ppm_scale()  # Get ppm scale from the first spectrum

                # Normalize the intensity data for the heatmap
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

            # Add the NMR heatmap to the first subplot
            fig.add_trace(go.Heatmap(
                x=list(reversed(filtered_ppm_values)),
                y=nmr_times,  # Replace heatmap_times with nmr_times
                z=filtered_heatmap_intensity,
                colorscale='Viridis',
                showscale=False),
                row=1, col=1
            )

            # Add the voltage trace to the second subplot
            fig.add_trace(go.Scatter(
                x=filtered_df['Ewe'],
                y=filtered_df['absolute_time'],
                mode='lines'),
                row=1, col=2
            )

            # Update layout
            fig.update_layout(
                title="NMR Spectra and Voltage Trace",
                xaxis1_title="Chemical Shift (ppm)",
                xaxis2_title="Voltage (V)",
                yaxis_title="Time"
            )

            # Find the first and last spectra
            first_spectrum_path, last_spectrum_path = find_first_last_spectra(nmr_folder, '19F')

            # Define a figure for the spectra
            spectra_fig = go.Figure()

            # Initialize variables for offset
            offset_value = 1000000  # Adjust this value as needed for visibility

            for idx, path in enumerate([first_spectrum_path, last_spectrum_path]):
                if path:
                    dic, data, sw, obs, car, label = read_varian_lowmem(path)
                    dic, data, _, _ = process_nmr_data(dic, data, sw, obs, car, apply_autophase=True)
                    uc = ng.pipe.make_uc(dic, data)
                    ppm = uc.ppm_scale()
                    intensity = data.real

                    # Apply offset to the second spectrum
                    offset = offset_value if idx > 0 else 0

                    spectra_fig.add_trace(go.Scatter(
                        x=list(reversed(ppm)),  # Reverse the x-axis
                        y=intensity + offset, mode='lines',
                        name=f'Spectrum {idx + 1} ({os.path.basename(path)})'))

            spectra_fig.update_layout(
                title=f"First and Last NMR Spectra ({nmr_start_time.strftime('%Y-%m-%d %H:%M:%S')} - {nmr_end_time.strftime('%Y-%m-%d %H:%M:%S')})",
                xaxis_title="Chemical Shift (ppm)",
                yaxis_title="Intensity"
            )

            return fig, spectra_fig

        except Exception as e:
            print(f"Error: {e}")
            return go.Figure(), go.Figure()
