import datetime
import nmrglue as ng
import os
import utils
import eclabfiles as ecf
import pandas as pd
from galvani import BioLogic
from datetime import datetime, timedelta


def extract_date_time(file_path):
    # Extract the part of the directory name that contains the date and time
    try:
        date_time_str = file_path.split(os.sep)[-1].split('_')[1].split('.')[0]
        return datetime.datetime.strptime(date_time_str, "%Y%m%dT%H%M%S")
    except (IndexError, ValueError):
        # Handle cases where the date and time cannot be extracted
        return None


def find_spectra_in_range(directory, start_date, end_date, nucleus):
    spectra_paths = []
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            if dir_name.endswith(".fid"):
                file_path = os.path.join(root, dir_name)
                file_date_time = extract_date_time(file_path)
                if (file_date_time and start_date <= file_date_time <= end_date and
                        file_path.split(os.sep)[-1].startswith(nucleus)):
                    spectra_paths.append(file_path)
    return spectra_paths

def read_nmr_data_lowmem(base_dir, format_type):
    if format_type == 'Varian':
        return read_varian_lowmem(base_dir)
    elif format_type == 'Bruker':
        return read_bruker_lowmem(base_dir)
    else:
        raise ValueError(f"Unsupported NMR data format: {format_type}")

def read_varian_lowmem(base_dir):
    """Read Varian data as low-memory objects."""
    dic, data = ng.varian.read(base_dir)
    procpar = ng.varian.read_procpar(base_dir + "/procpar")
    sw = float(procpar['sw']['values'][0])
    obs = float(procpar['sfrq']['values'][0])
    rfl = float(procpar['rfl']['values'][0])
    car = (sw / 2)-rfl
    label = procpar['tn']['values'][0]
    runtime_str = procpar['time_run']['values'][0]
    runtime = datetime.datetime.strptime(runtime_str, "%Y%m%dT%H%M%S")
    return dic, data, sw, obs, car, label, runtime

def read_bruker_lowmem(base_dir):
    """Read Bruker data as low-memory objects."""
    return dic, data, sw, obs, car, label, runtime


def process_nmr_data(dic, data, sw, obs, car, nmr_format, runtime, apply_autophase=True, p0=0.0, p1=0.0):
    """Process NMR data with optional autophasing, adaptable to different NMR formats."""

    # Set up parameters
    if nmr_format == 'Varian':
        udic = ng.varian.guess_udic(dic, data)
    elif nmr_format == 'Bruker':
        udic = ng.bruker.guess_udic(dic, data)
    else:
        raise ValueError(f"Unsupported NMR format: {nmr_format} proc")

    udic[0]['size'] = data.shape[0]
    udic[0]['complex'] = True
    udic[0]['encoding'] = 'direct'
    udic[0]['sw'] = sw
    udic[0]['obs'] = obs
    udic[0]['car'] = car
    udic[0]['runtime'] = runtime

    # Convert to NMRPipe format and process
    C = ng.convert.converter()
    if nmr_format == 'Varian':
        C.from_varian(dic, data, udic)
    elif nmr_format == 'Bruker':
        C.from_bruker(dic, data, udic)

    dic, data = C.to_pipe()
    dic, data = ng.pipe_proc.em(dic, data, lb=1)
    dic, data = ng.pipe_proc.zf(dic, data, auto=True)
    dic, data = ng.pipe_proc.ft(dic, data, auto=True)

    # Autophase if needed
    if apply_autophase:
        data, phase_params = ng.proc_autophase.autops(data, 'acme', return_phases=True)
        p0, p1 = phase_params
    else:
        dic, data = ng.process.pipe_proc.ps(dic, data, p0=p0, p1=p1)

    return dic, data, p0, p1

def eclab_voltage(processed_voltage_df, start_time, end_time):
    # Ensure start_time and end_time are in datetime format
    start_time = pd.to_datetime(start_time)
    end_time = pd.to_datetime(end_time)

    # Filter DataFrame between start_time and end_time
    volt_df = processed_voltage_df[
        (processed_voltage_df['absolute_time'] >= start_time) & (processed_voltage_df['absolute_time'] <= end_time)]

    return volt_df

def process_eclab(directory):

    print('Processing MPR file for capacity plot')

    eclabfiles = utils.identify_eclab_files(directory)
    mpr_file_path = eclabfiles[0]
    mpl_file = eclabfiles[1]
    mpr_file = BioLogic.MPRfile(mpr_file_path)
    df = pd.DataFrame(mpr_file.data)

    def extract_start_time(mpl_file_path):
        # Extracts the start time from an MPL file
        with open(mpl_file_path, 'r', encoding='ISO-8859-1') as file:
            for line in file:
                if line.startswith('Acquisition started on :'):
                    timestamp = line.split(':')[1].strip()
                    return pd.to_datetime(timestamp)

    # Convert 'Q charge/discharge' values to absolute values
    df['Abs_Q_charge_discharge'] = df['Q charge/discharge/mA.h'].abs()

    # Map half cycles to full cycle numbers, ensuring half cycles 0 and 1 are mapped to full cycle 1
    df['Full_Cycle_Number'] = ((df['half cycle'] // 2) + 1).astype(int)

    is_charge = df['half cycle'] % 2 == 0  # If first cycle (0) is charge, then this is true
    is_discharge = ~is_charge  # The opposite for discharge cycles

    charge_capacity = df[is_charge].groupby('Full_Cycle_Number')['Abs_Q_charge_discharge'].max()
    discharge_capacity = df[is_discharge].groupby('Full_Cycle_Number')['Abs_Q_charge_discharge'].max()

    coulombic_efficiency = (discharge_capacity / charge_capacity) * 100

    #absolote time handling
    start_time = extract_start_time(mpl_file)
    df['Absolute_Time_UTC'] = df['time/s'].apply(lambda s: start_time + timedelta(seconds=s))

    time = df.groupby('Full_Cycle_Number')['time/s'].max()
    time_utc = df.groupby('Full_Cycle_Number')['Absolute_Time_UTC'].max()

    cycle_numbers = charge_capacity.index.union(discharge_capacity.index)
    processed_cycle_df = pd.DataFrame({
        'Cycle_Number': cycle_numbers,
        'Charge_Capacity': charge_capacity.reindex(cycle_numbers, fill_value=0),
        'Discharge_Capacity': discharge_capacity.reindex(cycle_numbers, fill_value=0),
        'Coulombic Efficiency': coulombic_efficiency.reindex(cycle_numbers, fill_value=100),  # Default to 100% efficiency if no data
        'Time': time.reindex(cycle_numbers, fill_value=0),
        'Timestamp': time_utc.reindex(cycle_numbers, fill_value=0)
    })

    full_time = df['time/s']
    full_volt = df['Ewe/V']
    full_time_utc = df['Absolute_Time_UTC']
    processed_voltage_df = pd.DataFrame({
        'Time':full_time,
        'Timestamp':full_time_utc,
        'Voltage':full_volt
    })
    print(processed_cycle_df, processed_voltage_df)
    return processed_cycle_df, processed_voltage_df