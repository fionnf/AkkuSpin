import datetime
import nmrglue as ng
import os
import utils
import eclabfiles as ecf
import pandas as pd


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

    # Generate UID based on relevant parameters (adjust as needed)
    uid = utils.generate_uid(nmr_format, obs, car, runtime)  # Implement generate_uid accordingly

    # Use the cache_dir from utils.py
    cache_file_path = os.path.join(utils.cache_dir, f'{uid}.pkl')

    # Check if cached data exists
    if os.path.exists(cache_file_path):
        with open(cache_file_path, 'rb') as cache_file:
            return pickle.load(cache_file)  # Return cached results

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

    # Cache the results
    with open(cache_file_path, 'wb') as cache_file:
        pickle.dump((dic, data, p0, p1), cache_file)

    return dic, data, p0, p1

def process_eclab_files(directory, start_time, end_time):
    eclabfiles = utils.identify_eclab_files(directory)
    mpr_file = eclabfiles[0]
    mpl_file = eclabfiles[1]

    df = ecf.to_df(mpr_file)
    ecl_start_time = utils.extract_start_time(mpl_file)
    df['absolute_time'] = pd.to_timedelta(df['time'], unit='s') + ecl_start_time
    volt_df = df[(df['absolute_time'] >= start_time) & (df['absolute_time'] <= end_time)]

    return volt_df


def process_mpr_capacity(directory):
    print('Processing mpr file for capacity plot')
    eclabfiles = utils.identify_eclab_files(directory)
    mpr_file = eclabfiles[0]

    df = ecf.to_df(mpr_file)

    # Convert 'Q charge/discharge' values to absolute values
    df['Abs_Q_charge_discharge'] = df['Q charge/discharge']

    # Map half cycles to full cycle numbers, ensuring half cycles 0 and 1 are mapped to full cycle 1
    df['Full_Cycle_Number'] = ((df['half cycle'] // 2) + 1).astype(int)

    # Calculate charge and discharge capacities
    charge_capacity = df[(df['mode'] == 1) & (df['ox/red'] == 1)].groupby('Full_Cycle_Number')['Abs_Q_charge_discharge'].max()
    discharge_capacity = df[(df['mode'] == 1) & (df['ox/red'] == 0)].groupby('Full_Cycle_Number')['Abs_Q_charge_discharge'].min().abs()
    coulombic_efficiency = (discharge_capacity / charge_capacity) * 100

    time = df.groupby('Full_Cycle_Number')['time'].max()

    last_uts = df.groupby('Full_Cycle_Number')['uts'].last()

    cycle_numbers = charge_capacity.index.union(discharge_capacity.index)
    processed_df = pd.DataFrame({
        'Cycle_Number': cycle_numbers,
        'Charge_Capacity': charge_capacity.reindex(cycle_numbers, fill_value=0),
        'Discharge_Capacity': discharge_capacity.reindex(cycle_numbers, fill_value=0),
        'Coulombic Efficiency': coulombic_efficiency.reindex(cycle_numbers, fill_value=0),
        'Time': time.reindex(cycle_numbers, fill_value=0),
        'Last_UTS': last_uts.reindex(cycle_numbers, fill_value=0)
    })

    #Printing
    #pd.set_option('display.max_columns', None)
    #pd.set_option('display.width', None)
    #print(processed_df)
    return processed_df
