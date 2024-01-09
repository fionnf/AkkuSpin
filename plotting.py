import plotly.graph_objs as go
from plotly.subplots import make_subplots


def create_nmr_heatmap(ppm_values, nmr_times, heatmap_intensity):
    fig = make_subplots(rows=1, cols=1)

    fig.add_trace(go.Heatmap(
        x=list(reversed(ppm_values)),
        y=nmr_times,
        z=heatmap_intensity,
        colorscale='Viridis',
        showscale=False),
    )

    fig.update_layout(
        #title="NMR Heatmap",
        xaxis_title="Chemical Shift (ppm)",
        yaxis_title="Time"
    )

    return fig


def create_voltage_trace(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Ewe'],
        y=df['absolute_time'],
        mode='lines'),
    )

    fig.update_layout(
        title="Voltage Trace",
        xaxis_title="Voltage (V)",
        yaxis_title="Time"
    )

    return fig


def create_spectra_fig(first_spectrum_path, last_spectrum_path):
    fig = go.Figure()

    offset_value = 1000000

    for idx, path in enumerate([first_spectrum_path, last_spectrum_path]):
        if path:
            dic, data, sw, obs, car, label = data_processing.read_varian_lowmem(path)
            dic, data, _, _ = data_processing.process_nmr_data(dic, data, sw, obs, car, format_type,
                                                               apply_autophase=True)
            uc = ng.pipe.make_uc(dic, data)
            ppm = uc.ppm_scale()
            intensity = data.real

            offset = offset_value if idx > 0 else 0

            fig.add_trace(go.Scatter(
                x=list(reversed(ppm)),
                y=intensity + offset,
                mode='lines',
                name=f'Spectrum {idx + 1} ({os.path.basename(path)})')
            )
            fig.update_xaxes(autorange="reversed")

    fig.update_layout(
        title=f"First and Last NMR Spectra ({nmr_start_time.strftime('%Y-%m-%d %H:%M:%S')} - {nmr_end_time.strftime('%Y-%m-%d %H:%M:%S')})",
        xaxis_title="Chemical Shift (ppm)",
        yaxis_title="Intensity"
    )

    return fig
