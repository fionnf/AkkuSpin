import datetime
import nmrglue as ng
import os

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

def read_varian_lowmem(base_dir):
    """Read Varian data as low-memory objects."""
    dic, data = ng.varian.read(base_dir)
    procpar = ng.varian.read_procpar(base_dir + "/procpar")
    sw = float(procpar['sw']['values'][0])
    obs = float(procpar['sfrq']['values'][0])
    car = -sw / 2  # Assuming the carrier is at the midpoint of sw
    label = procpar['tn']['values'][0]
    return dic, data, sw, obs, car, label

def process_nmr_data(dic, data, sw, obs, car, apply_autophase=True, p0=0.0, p1=0.0):
    """Process NMR data with optional autophasing."""
    # Set up parameters
    udic = ng.varian.guess_udic(dic, data)
    udic[0]['size'] = data.shape[0]
    udic[0]['complex'] = True
    udic[0]['encoding'] = 'direct'
    udic[0]['sw'] = sw
    udic[0]['obs'] = obs
    udic[0]['car'] = car

    # Convert to NMRPipe format and process
    C = ng.convert.converter()
    C.from_varian(dic, data, udic)

    # Processing steps
    dic, data = C.to_pipe()
    dic, data = ng.pipe_proc.zf(dic, data, auto=True)
    dic, data = ng.pipe_proc.ft(dic, data, auto=True)
    data *= 800
    dic, data = ng.pipe_proc.em(dic, data, lb=0.5)

    # Autophase if needed
    if apply_autophase:
        data, phase_params = ng.proc_autophase.autops(data, 'acme', return_phases=True)
        p0, p1 = phase_params  # Unpack the phase parameters
    else:
        # Apply the same phasing parameters (p0, p1) from the first spectrum
        dic, data = ng.process.pipe_proc.ps(dic, data, p0=p0, p1=p1)

    return dic, data, p0, p1
