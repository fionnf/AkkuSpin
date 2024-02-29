# AkkuSpin

## Overview
AkkuSpin is a web-based application designed for visualizing and analyzing battery cycling data in conjunction with NMR (Nuclear Magnetic Resonance) spectroscopy results. This tool aims to provide comprehensive insights into battery performance and characteristics through interactive data visualization.

## Features
- **NMR Data Visualization**: Interactive plots displaying NMR spectra captured over time. 
- **Battery Cycling Data Analysis**: Visualization of battery charge/discharge cycles with support for ECLab files.  
- **Data Integration**: Combines NMR and battery cycling data for in-depth analysis.
- **User-Friendly Interface**: Easy to navigate interface for both technical and non-technical users.

## Installation
- **Install Python**: https://www.python.org/
- **Install dependencies (packages)**: ECLabFiles, numpy, nmrglue, dash, plotly, pandas, hashlib, shelve. Note, this program uses a modified version of the [galvani](https://github.com/echemdata/galvani) package so live ECLab files can be plotted, so the galvani package does not need to be installed. 
- **Run the main.py script**

## Usage
Akkuspin looks at datasets of NMR data captured over time, the directory names of each spectrum contain a timestamp which is interpreted by the program, therefore creating a time based plot.
The acquisition of spectra in Varian systems has been documented below. 
Depending on the methods of arrayed spectral acquisition, the code may need to be altered. 
A current working point is to make it possible to input the timestamp format therefore allowing for different timestamp identifiers.

Note: The plotted timestamp for NMR spectra is always the runtime of the actual spectrum which may be different to when the directory holding the spectrum was created.

Currently, Akkuspin has only been implemented for Varian NMR data, however an empty function has been created for Bruker data and implementing other file formats should not be too difficult. 
Please provide test data from your NMR systems.

### Acquisition of Spectra
- Akkuspin is designed to view large sets of NMR data while keeping processing and plotting times low.
- Spectra need to be captured with timestamps formatted in the spectral directories, Accuspin uses the following by default as a subdirectory name for each spectrum in the array: nucleus_YYYYMMDDThhmmss.fid
- **Varian Systems** for Varian NMR systems, spectra can be acquired using the VNMRJ cpommand : listenon to recieve talk commands See VNMRJ_array.sh for an example script.


## License
MIT Licence as described in Licence file. 

## Contact
For any queries or suggestions, please contact us at [akkuspin@fionnferreira.com](akkuspin@fionnferreira.com).

