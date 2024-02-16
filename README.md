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
- **Install dependencies using pip**: ECLabFiles, numpy, nmrglue, dash, plotly

## License
MIT Licence as described in Licence file. 

## Contact
For any queries or suggestions, please contact us at f.m.eckardt.ferreira@student.rug.nl.

## Acquisition of Spectra

- Accuspin is designed to view large sets of NMR data while keeping processing and plotting times low.
- Spectra need to be captured with timestamps formatted in the spectral directories, Accuspin uses the following by default as a subdirectory name for each spectrum in the array: nucleus_YYYYMMDDThhmmss.fid
- **Varian Systems** for Varian NMR systems, spectra can be acquired using the VNMRJ cpommand : Talk. See VNMRJ_array.sh for an example script.
