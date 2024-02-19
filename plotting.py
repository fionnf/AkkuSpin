import plotly.graph_objs as go
from plotly.subplots import make_subplots
import data_processing
import nmrglue as ng
import os
import numpy as np


def create_nmr_heatmap(ppm_values, nmr_times, heatmap_intensity):
    fig = make_subplots(rows=1, cols=1)

    fig.add_trace(go.Heatmap(
        x=list(reversed(ppm_values)),
        y=nmr_times,
        z=heatmap_intensity,
        colorscale='Viridis',
        showscale=False),
    )

    fig.update_xaxes(autorange="reversed")

    fig.update_layout(
        title="NMR Data and Voltage Trace",
        xaxis_title="Chemical Shift (ppm)",
        yaxis_title="Time"
    )
    return fig


def create_voltage_trace(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Ewe'],
        y=df['absolute_time'],
        mode='lines',
        line=dict(color='Red')
    ))

    fig.update_layout(
        title="Voltage Trace",
        xaxis_title="Voltage (V)",
        yaxis_title="Time"
    )

    return fig



def create_spectra_fig(first_spectrum_path, last_spectrum_path, format_type, nmr_start_time, nmr_end_time):
    spectra_fig = go.Figure()

    for idx, path in enumerate([first_spectrum_path, last_spectrum_path]):
        if path:
            dic, data, sw, obs, car, label, runtime = data_processing.read_nmr_data_lowmem(path, format_type)
            dic, data, _, _ = data_processing.process_nmr_data(dic, data, sw, obs, car, format_type, runtime,
                                                               apply_autophase=True)
            uc = ng.pipe.make_uc(dic, data)
            ppm = uc.ppm_scale()
            intensity = data.real

            spectra_fig.add_trace(go.Scatter(
                x=list((ppm)),
                y=intensity, mode='lines',
                name=f'Spectrum {idx + 1} ({os.path.basename(path)})')
            )

            spectra_fig.update_xaxes(autorange="reversed")

    spectra_fig.update_layout(
        title=f"First and Last NMR Spectra ({nmr_start_time.strftime('%Y-%m-%d %H:%M:%S')} - {nmr_end_time.strftime('%Y-%m-%d %H:%M:%S')})",
        xaxis_title="Chemical Shift (ppm)",
        yaxis_title="Intensity"
    )

    return spectra_fig

def create_3d_fid_plot(base_dir, format_type):

    dic, data, sw, obs, car, label, runtime = data_processing.read_nmr_data_lowmem(base_dir, format_type)

    time_points = np.linspace(0, len(data)/sw, len(data))

    # Create a 3D scatter plot
    fid_fig = go.Figure(data=[go.Scatter(
        x=time_points,   # Time
        y=data.real,     # Real part of the FID
        #z=data.imag,     # Imaginary part of the FID
        mode='lines',
        #marker=dict(
            #size=2,
            #opacity=0.8
        #)
    )])

    fid_fig.update_layout(title='Real FID', autosize=True, xaxis_title='Time (s)', yaxis_title='Intensity',
                      margin=dict(l=65, r=50, b=65, t=90))

    return fid_fig


def plot_cycling_data(directory, theoretical_capacity):
    # Call the processing function to get the data ready for plotting
    output = data_processing.process_cycling_data(directory, theoretical_capacity,charge_step_id=1, discharge_step_id=2)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=output['cycle_numbers'], y=output['max_charge_cycle'], mode='markers', name='Normalized Charge Capacity',
                   marker_color='green'),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=output['cycle_numbers'], y=output['max_discharge_cycle'], mode='markers', name='Normalized Discharge Capacity',
                   marker_color='blue'),
        secondary_y=True,
    )
    fig.update_layout(
        xaxis_title='Cycle Number',
    )

    fig.update_yaxes(title_text='Charge Capacity (%)', secondary_y=False, color='green')
    fig.update_yaxes(title_text='Discharge Capacity (%)', secondary_y=True, color='blue')

    return fig