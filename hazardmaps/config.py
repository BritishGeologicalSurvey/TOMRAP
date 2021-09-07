# CONFIG FILE

DATADIR = "path"
weightings = ["foo", "bar"]

# etc...

DATADIR = "../datadir/"
# The one above is not found in the data folder - DV added on Friday - was in the other folder
#expofile = DATADIR + "TZA_buildings_exposure_20200731.dbf" #contains location id and positions  - present
expofile = DATADIR + "TZA_buildings_exposure_20200224.dbf" #contains location id and positions  - present
expobfile = DATADIR + "TZA_buildings_exposure_breakdown_20200731.dbf" 
#contains location id and breakdown of number of each house type
#volcP = ["kyejo", "meru"]
#volcL = ["lengai", "ngozi", "rungwe"]
volcfile = DATADIR + "World_Volcanoes_Smithsonian_Institution_GVP.shp" #point locations of volcanoes
volcnames = ["Lengai, Ol Doinyo", "Meru", "Ngozi", "Rungwe", "Kyejo"] #names of volcanoes in Smithsonian shp

# 1 in 100, 1 in 200 in the file
floodratio = 100 # selects from different flood tifs
floodtypes = ["FD", "FU", "P"]  #selects from different flood tifs