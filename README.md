# TOMRAP – Tool for Multi-hazard Risk Assessment in Python

*Description from the original IFF proposal**

The project builds on outputs from the METEOR project (NEE6423R) to generate a tool that can be used in future projects to assess multi-hazard risk. The METEOR model was initially developed in ArcGIS. By streamlining this code in Python we will make multi-hazard risk analysis faster and more widely applicable.

This software was developed from a jupyter notebook by @kle (Kathryn Leeming) to take multiple spatial inputs (dbf, tifs) and combine them to create hazard vulternability maps.

Notebook was run from a directory containing copies of the files, original files are on W drive. The original notebooks are now archived in the `notebooks` directory.


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

### Data location

There are a large number of data files required to run the analysis, in the current version, these should be placed in the same location (all in the same folder). The location of this folder is specified in `config.py` under the `DATADIR` variable. 

You may place the data in a different location/drive, and symbolically link to the folder as well, if you are using linux/unix.


### Config file

The config file is where the input file names, and other parameters are set. A working example is saved under `config_tanzania.py` - however - you should rename this to `config.py` when you wish to use it. This allows us to keep records/backups of the parameters for future model runs, e.g. `config_nepal.py`, `config_tanzania.py` etc...


#### Config file parameters

Here is a brief description of the current  `config.py` parameters. Standard Python syntax is used, i.e. the parameter value is assigned using an `=` sign. Values can be strings (in quote marks), and some are lists: `['item1', 'item2', ...etc]`. Truth values are set to either `True` or `False`. 


 - `DATADIR`  - this is the base data directory. It should be a string. These can either be absolute or relative file paths in Windows or Unix format depending on the platform being used.

For the following input file names, I tend to use the baseline `DATADIR` and then append the file name to create a string, for example:

`exposure_file = DATADIR + "TZA_buildings_exposure_20200224.dbf"`

**Input Files**

 - `exposure_file`  - Building exposure
 - `exposure_breakdown_file`  - Building exposure breakdown/metadata
 - `eearthquake_file`  -  Earthquake data
 - `volcfile`  - Volcano data point data

**Parameters**

 - `volcnames`  - a Python list of names of volcanoes in the Volcano shapefile (you would need to inspect the shapefile first or know the naming conventions used.)
 - `floodratio`  -  A number that sets the interval of the flood ratios, e.g. 1 in 100 etc. 
 - `floodtypes`  -  A list of strings that specifies the flood types to be used in the analysis. e.g. FU, FD, P

 - `figure_prefix`  - a string that is appended to the start of the output figures (if required)
 - `plot_types`  - a list of strings that specifies the types of plots that will be produced. The full list would be:

```
plot_types = ["ear", "plu", "flu", "tep", "lahar", "pgaindx", "P", "FU", "lah", "pyr", "equ", "flood", "volc", "hmap"]
```

But if you simply wanted to make a single plot, you can pass a single string, e.g.:
 
```
plot_types = "hmap"
```

 - `building_type_tz`  -  This is a list of the building types and codes that correspond to the columns loaded from the buildings.dbf file. You would need to inspect this first to see what the column names are as they vary between datasets.
