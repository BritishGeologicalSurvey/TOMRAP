# CONFIG FILE
# Tanzania

SEISMIC = True
FLOODING = True 
VOLCANIC = True
LANDSLIDE = False
EXPOSURE = True

# This is a bit of a workaround if your flood data
# triggers an index error, this can be due to swapping the
# x and y coordinates. The Nepa data requires this to be true 
# but not Tanzania
invert_flood_tiff = False

DATADIR = "../datadir/Tanzania/"
# The one above is not found in the data folder - DV added on Friday - was in the other folder
#config.exposure_file = config.DATADIR + "TZA_buildings_exposure_20200731.dbf" #contains location id and positions  - present
exposure_file = DATADIR + "TZA_buildings_exposure_20200224.dbf" #contains location id and positions  - present
exposure_breakdown_file = DATADIR + "TZA_buildings_exposure_breakdown_20200731.dbf" 
#contains location id and breakdown of number of each house type
#volcP = ["kyejo", "meru"]
#volcL = ["lengai", "ngozi", "rungwe"]
volcfile = DATADIR + "World_Volcanoes_Smithsonian_Institution_GVP.shp" #point locations of volcanoes
volcnames = ["Lengai, Ol Doinyo", "Meru", "Ngozi", "Rungwe", "Kyejo"] #names of volcanoes in Smithsonian shp

# 1 in 100, 1 in 200 in the file
floodratio = 100 # selects from different flood tifs
floodtypes = ["FD", "FU", "P"]  #selects from different flood tifs
# in the Seismic folder
eearthquake_file = DATADIR + "hazard_map_mean_tanzania.dbf" #contains earthquake information

figure_prefix = "output_"
#plot_types = ["ear", "plu", "flu", "tep", "lahar", "pgaindx", "P", "FU", "lah", "pyr", "equ", "flood", "volc", "hmap"]
# OVERWRITE QUICK TEST
plot_types = "hmap"

# TANZANIA
# These should come from the vuln curves
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

# Numbers could be no. of floors
# Could be made more general. Could be different in UK for e.g.
