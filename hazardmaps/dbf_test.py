# dbf_test.py
import geopandas as gpd
from hazardmap import getbreakdown, dbf_to_df

import config as config

tz_buildings = getbreakdown(config.exposure_breakdown_file)
tz_withgeometry = dbf_to_df(config.exposure_file)