Configuration
=============

Further configuration details can be added here when the functionality becomes available.

Here we will take a look at the `conf.py` file to see how to configure the hazardmap settings and data sources:

Hazard options
--------------

These flags (True/False) determine which hazard inputs will be
used to calculate the overall hazard map at the end.

::

  SEISMIC = True
  FLOODING = True 
  VOLCANIC = True
  LANDSLIDE = False
  EXPOSURE = True


Custom vulnerability curve
--------------------------

Setting this to true will make the TOMRAP tool look for 
a csv file that defines vulnerability rating curves by
building type as a csv file.

An example custom vulnerability curve is located in the repository here:

`Example vulnerability curve for Tanzania buildings <https://kwvmxgit.ad.nerc.ac.uk/python/hazardmaps/-/raw/master/example_data/vuln_curve_sample.csv?inline=false>`_

Vulnerability curves work in place of the list of building weights found at the bottom of the config file. 
(See further down this document.) Instead of using the same multiplier for every building type in all cases,
the user can specifiy a hazard likelihood in this config file (`hazard_intensity`) and then the weighting for
that specific likelihood is read from the vulnerability curve supplied. TOMRAP does not require the exact 
hazard intensity specified to match the values supplied in the vulnerability curve. For example, if you specify 
a hazard intensity in the config file here that falls between two points in the csv file, TOMRAP will choose the
closest matching value in the csv file. The `vuln_curve_file` is relative to the `DATADIR` directory. 

::

  CUSTOM_VULN_CURVE = True

  hazard_intensity = 2.0    
  vuln_curve_file = "vuln_curve_example.csv"


See also the section on `Calculating vulnerability curves <http://python.glpages.ad.nerc.ac.uk/hazardmaps/modeldetail.html#defining-weights-by-vulnerability-curve>`_


Invert coordinates
------------------

This is a bit of a workaround if your flood data
triggers an index error, this can be due to swapping the
x and y coordinates. The Nepa data requires this to be true 
but not Tanzania

::

  invert_flood_tiff = False


Data locations and types
-------------------------

:: 

  
  DATADIR = "../datadir/Tanzania/"
  # The one above is not found in the data folder - DV added on Friday - was in the other folder
  #config.exposure_file = config.DATADIR + "TZA_buildings_exposure_20200731.dbf" #contains location id and positions  - present
  exposure_file = DATADIR + "TZA_buildings_exposure_20200731.dbf" #contains location id and positions  - present
  exposure_breakdown_file = DATADIR + "TZA_buildings_exposure_breakdown_20200731.dbf" 


Volcano data specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~

`volcP` is a list of volcano code names used to calculate Pyroclastic flow hazards.

`volcL` is a list of volcano code names used to calculate Lahar hazards.

`volcfile` is the shapefile containing the volcano point data (referenced by the code names). 
You would have to inspect this file first to retrieve the code names used.

`volcnames` is a list of all the volcanos used in the analysis.

:: 

  volcP = ["kyejo", "meru"]
  volcL = ["lengai", "ngozi", "rungwe"]
  volcfile = DATADIR + "World_Volcanoes_Smithsonian_Institution_GVP.shp" 
  volcnames = ["Lengai, Ol Doinyo", "Meru", "Ngozi", "Rungwe", "Kyejo"]


Flood data specifications
~~~~~~~~~~~~~~~~~~~~~~~~~

`flood_ratio` refers to the return period of the flood data you have. So if you have a series
of flood TIFFs separated by 100 year return period intervals, you would specificy "100" here.

The filenames must match the structure below, i.e.

`FLOODTYPE_1inXXX.tif`, e.g `PU_1in100.tif`  (that's a one not an L, i.e. "one in a hundred")

::

  PU_1in100.tif    # One in 100 year pluvial flood map
  PU_1in200.tif    # One in 200 year pluvial flood map
  PU_1in300.tif

  FD_1in100.tif    # One in 100 year fluvial (defended) flood map
  FD_1in200.tif
  FD_1in300.tif
  ..and so on

Should be specified in the config file as:

::

  # 1 in 100, 1 in 200 in the file
  floodratio = 100 # selects from different flood tifs
  floodtypes = ["FD", "FU", "P"]  #selects from different flood tifs

`floodtypes` is a list of codes for the type of flood in the tiff.

**P** - Pluvial

**FD** - Fluvial - defended

**FU** - Fluvial - undefended


Earthquake data supplementary info
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At present, the only parameter needed is the earthquake file DBF file. 

::

  eearthquake_file = DATADIR + "hazard_map_mean_tanzania.dbf"   (yes that is two Es in eearthquake...)


Output plot files
-----------------

The `figure_prefix` option simply appends some text to the start of every output figure
to help with organising your files later. It can be left as an empty string to append no
text: `''` if you prefer.

The `plot_types` is a python list of the various plot types supported by TOMRAP. You can specify as
many or as few as you like. 

::

  figure_prefix = "output_"
  plot_types = ["ear", "plu", "flu", "tep", "lahar", "pgaindx", "P", "FU", "lah", "pyr", "equ", "flood", "volc", "hmap"]

The plot type codes are explained in the table below:

========== ==========================
Plot code  Explanation
========== ==========================
ear        Earthquake
plu        Pluvial
flu        Fluvial
tep        Tephra
lahar      Lahars
P          ---
FU         ---
pgaindx    Peak Ground Acceleration
pyr        Pyroclastic flows
equ        Combined Earthquake Hazard
flood      Combined Flood Hazard
volc       Combined Volcanic Hazard
hmap       Combined All Hazards
========== ==========================

Pluvial Flooding is that caused by rainfall alone, Fluvial flooding is that which is caused by
the overflowing of a water body (a river, for example.)

`hmap` is the "final" combined hazard map, though you may have use cases where you want to 
produce the component hazard risks as well.



Building types
--------------

`building_type_tz`

The building type codes are used to calculate risk based on building
type, either from the values specified in the config file, or the vulnerability curve
csv file supplied. The codes below should match the ones in the dbf files. 

::


  building_type_tz = ['CR/LFM/HBET:1,3',
                      'CR/LFM/HBET:4,7',
                      'CR/LFM/HBET:8,20',
                      'CR/LFINF+DNO/HBET:1,3',
                      'CR/LFINF+DNO/HBET:4,7', 
                      'CR/LFINF+DNO/HBET:8,20',
                      'S',                     
                      'MUR+CB99/HBET:1,3',
                      'MUR+CB99/HBET:4,7',
                      'W',
                      'MATO/LN', 
                      'MUR+ADO/HBET:1,3',
                      'MUR+CL99', 
                      'MUR+STRUB',
                       'W+WWD']


Manual weightings
-----------------

The set of weightings at the end of the config file is used to set the building weights for each type.

The order of the list for each type matches that in the `building_type_tz` list above. So each item in the 
list is an element-wise weight for the building type. Therefore, the lists below have to be the same length 
as the `building_type_tz` list above. Note that each hazard type has a separate weighting list. Currently 
only earthquakes can be set to have a vulnerability curve defined in a csv file, as of May 2022, you must set
the other hazard weighting types using this list method below. You may set weights to be the same by using the
syntax `tz_weight_fluvial = tz_weight_pluvial` for example, to set fluvial and pluvial weightings to use the
same weights if you wanted to.

::

  # Building type weightings
  tz_weight_pluvial = [0.32, 0.2, 0.12, 0.4, 0.25, 0.15, 0.09, 0.4, 0.25, 0.8, 0.56, 0.56, 0.56, 0.56, 0.56]
  tz_weight_fluvial = tz_weight_pluvial
  tz_weight_tephra = [0.3, 0.15, 0.09, 0.4, 0.2, 0.12, 0.09, 0.5, 0.25, 0.2, 0.6, 0.6, 0.6, 0.6, 0.6]
  tz_weight_lahar = [0.06, 0.1, 0.06, 0.6, 0.3, 0.18, 0.3, 0.4, 0.2, 1, 1, 1, 1, 1, 1]
  tz_weight_pyro = [0.56, 0.63, 0.7, 0.64, 0.72, 0.8, 0.9, 0.72, 0.81, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8]
  tz_weight_earthquake = [0.12, 0.32, 0.16, 0.18, 0.48, 0.24, 0.2, 0.09, 0.24, 0.09, 0.3, 0.3, 0.3, 0.3, 0.3]

