from galvani import BioLogic

mpr_file_path = '/Users/fionnferreira/Downloads/BioLogic Files/flow_nmr/fw05_flow1_C01.mpr'

try:
    mpr_file = BioLogic.MPRfile("/Users/fionnferreira/Downloads/BioLogic Files/flow_nmr/fw05_flow1_C01.mpr")
    print("Header:", mpr_file.header)  # This reveals the structure
    print("Columns:", mpr_file.data.columns)
except Exception as e:
    print(f"Error loading MPR file: {e}")