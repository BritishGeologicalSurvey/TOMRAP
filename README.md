# HazardMaps

This project contains a jupyter notebook to take multiple spatial inputs (dbf, tifs) and combine them to create hazard vulternability maps.

Notebook was run from a directory containing copies of the files, original files are on W drive. 


## Installation Requirements

This repository should be cloned to your local machine. The software depends on some 3rd Party Python 
libraries to run. The easiest way to manage the installation of these is using a conda environment.
The list of required packages is given in environment.yml.

To create a conda environment once you have an installation of conda installed, you can run:

```
conda create -f environment.yml --name hazmap
conda activate hazmap
```

After using the software/script, you can deactivate this environment with

```
conda deactivate
```


## User Guide

The hazard mapping program takes inputs from Flood Hazard Maps, Earthquake Risk Data, Volcanic Hazard Data, and
building style and size information to generate a series of multi-hazard risk maps. 

The program is written in Python and is run from the terminal or command line with the command:

```
python hazardmap.py
```

This file is located in the `hazardmap` subdirectory of the top level repository folder.

The parameters and config settings are all read in from the `config.py` settings file in the `hazardmap` folder.




