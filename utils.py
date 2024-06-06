import datetime
import os
import pandas as pd
import hashlib


def get_most_recent_time(directory):
    most_recent_time = None
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            if dir_name.endswith(".fid"):
                try:
                    # Extract the date and time part from the directory name
                    date_time_str = dir_name.split('_')[1].split('.')[0]
                    file_date_time = datetime.datetime.strptime(date_time_str, "%Y%m%dT%H%M%S")
                    if most_recent_time is None or file_date_time > most_recent_time:
                        most_recent_time = file_date_time
                except (IndexError, ValueError):
                    # Skip if the date and time cannot be extracted
                    continue
    return most_recent_time


def find_first_last_spectra(directory, nucleus):
    spectra_paths = []
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            if dir_name.startswith(nucleus) and dir_name.endswith(".fid"):
                file_path = os.path.join(root, dir_name)
                spectra_paths.append(file_path)

    if not spectra_paths:
        return None, None

    # Sort the spectra based on their filenames
    spectra_paths.sort()
    return spectra_paths[0], spectra_paths[-1]  # Return first and last spectra

def identify_eclab_files(directory):
    contents = os.listdir(directory)

    mpr_file = None
    mpl_file = None
    for file in os.listdir(directory):
        if file.endswith('.mpr'):
            mpr_file = os.path.join(directory, file)
            print('MPR found')
        elif file.endswith('.mpl'):
            mpl_file = os.path.join(directory, file)
            print('MPL found')
    if not mpr_file:
        raise FileNotFoundError("MPR file not found in the provided folder.")

    return mpr_file, mpl_file


def generate_uid(path, nucleus, *args):
    # Combine path, nucleus, and any other arguments into a single string
    combined = f"{path}_{nucleus}_" + "_".join(map(str, args))

    # Use SHA-256 hashing to generate a unique identifier
    uid = hashlib.sha256(combined.encode()).hexdigest()

    return uid

def generate_text_content(integrated_values, times):
    content = "Timestamp, Integrated Value\n"
    for time, value in zip(times, integrated_values):
        content += f"{time},{value}\n"
    return content