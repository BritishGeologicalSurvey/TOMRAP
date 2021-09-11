# CONFIG FILE

DATADIR = "../datadir/"
# The one above is not found in the data folder - DV added on Friday - was in the other folder
#exposure_file = DATADIR + "TZA_buildings_exposure_20200731.dbf" #contains location id and positions  - present
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
plot_types = ["ear", "plu", "flu", "tep", "lahar", "pgaindx", "P", "FU", "lah", "pyr", "equ", "flood", "volc", "hmap"]
# OVERWRITE QUICK TEST
plot_types = "hmap"