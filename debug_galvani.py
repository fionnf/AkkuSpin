from galvani_mod import BioLogic

mpr_file_path = '/Users/fionnferreira/Downloads/BioLogic Files/flow_nmr/fw05_flow1_C01.mpr'

try:
    mpr_file = BioLogic.MPRfile(mpr_file_path)
    #print("Modules:", mpr_file.modules)
    print("Columns:", mpr_file.data.dtype.names)
    print("Shape:", mpr_file.data.shape)
except AttributeError as e:
    print(f"Attribute Error: {e}")
except Exception as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Error loading MPR file: {e}")