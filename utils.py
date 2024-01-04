import datetime
import os
import pandas as pd

def extract_start_time(mpl_file_path):
    # Extracts the start time from an MPL file
    with open(mpl_file_path, 'r', encoding='ISO-8859-1') as file:
        for line in file:
            if line.startswith('Acquisition started on :'):
                timestamp = line.split(':')[1].strip()
                return pd.to_datetime(timestamp)


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