import plotly.graph_objs as go
from plotly.subplots import make_subplots
import data_processing
import nmrglue as ng
import os
import numpy as np
import pandas as pd


def create_nmr_heatmap(ppm_values, nmr_times, heatmap_intensity, experiment_start_time):
    fig = go.Figure()

    # Calculate time since the start of the experiment
    time_since_start = [(t - experiment_start_time).total_seconds() / 3600 for t in nmr_times]  # Time in hours

    # Add heatmap trace
    fig.add_trace(go.Heatmap(
        x=ppm_values,
        y=time_since_start,
        z=heatmap_intensity,
        colorscale='Viridis',
        showscale=False
    ))

    # Update x-axis for ppm values
    fig.update_xaxes(
        title="Chemical Shift (ppm)",
        autorange="reversed",
        range=[ppm_values[-1], ppm_values[0]]
    )

    # Update y-axis to reflect time since start
    fig.update_yaxes(
        title="Experiment Time (h)"
    )

    # Update layout
    fig.update_layout(
        title="NMR Data Heatmap",
    )

    # Debugging: Print the number of spectra
    if isinstance(heatmap_intensity, list):
        print("NUMBER OF SPECTRA:", len(heatmap_intensity))

    return fig


def create_voltage_trace(df, experiment_start_time):
    # Calculate time since the start of the experiment
    df['time_since_start'] = (df['Timestamp'] - experiment_start_time).dt.total_seconds() / 3600

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add voltage trace
    fig.add_trace(go.Scatter(
        x=df['Voltage'],
        y=df['time_since_start'],  # Use time since start
        mode='lines',
        #name='Voltage Trace'
    ), secondary_y=False)

    # Add Q_minus_Q0 trace
    fig.add_trace(go.Scatter(
        x=df['Q_minus_Q0'],
        y=df['time_since_start'],  # Use time since start
        mode='lines',
        #name='Q_minus_Q0 Trace'
    ), secondary_y=False)

    fig.update_xaxes(
        title="Voltage (V)"
    )
    fig.update_yaxes(
        title="Experiment Time (h)",
        secondary_y=False
    )
    fig.update_layout(
        title="Voltage and Q_minus_Q0 Trace"
    )
    #fig.show()
    return fig


def create_spectra_fig(first_spectrum_path, last_spectrum_path, format_type, nmr_start_time, nmr_end_time):
    spectra_fig = go.Figure()

    for idx, path in enumerate([first_spectrum_path, last_spectrum_path]):
        if path:
            dic, data, p0, p1, runtime, obs, sw, car = data_processing.process_nmr_data(
                path=path,
                nmr_format=format_type,
                apply_autophase=True,
                p0=0,
                p1=0
            )
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


def plot_capacities_and_efficiency_eclab(directory):
    processed_df = data_processing.process_eclab(directory)
    processed_df = processed_df[0]

    # Create subplots: one y-axis for capacities, another for Coulombic Efficiency
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Plot Charge and Discharge Capacities
    fig.add_trace(go.Scatter(x=processed_df['Cycle_Number'], y=processed_df['Charge_Capacity'], mode='markers',
                             name='Charge Capacity', marker=dict(color='blue')), secondary_y=False)
    fig.add_trace(go.Scatter(x=processed_df['Cycle_Number'], y=processed_df['Discharge_Capacity'], mode='markers',
                             name='Discharge Capacity', marker=dict(color='red')), secondary_y=False)

    # Plot Coulombic Efficiency on secondary y-axis
    fig.add_trace(
        go.Scatter(x=processed_df['Cycle_Number'], y=processed_df['Coulombic Efficiency'], mode='markers',
                   name='Coulombic Efficiency', marker=dict(color='green')), secondary_y=True)

    # Set x-axis title
    fig.update_xaxes(title_text="Cycle Number",tickfont=dict(size=16), showgrid=False)

    # Set y-axes titles
    fig.update_yaxes(title_text="Capacity (mAh)", secondary_y=False, tickfont=dict(size=16), showgrid=False)
    fig.update_yaxes(title_text="Coulombic Efficiency (%)", secondary_y=True, tickfont=dict(size=16), showgrid=False)

    return fig