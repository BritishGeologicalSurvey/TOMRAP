# hazardmap.py
# This script takes different shape inputs and combines them to create a hazard vulnerability map.
import geopandas as gpd
import pandas as pd
import numpy as np
from osgeo import gdal
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from matplotlib.testing.decorators import image_comparison
import hazardmaps.config as config


def dbf_to_df(filename):
    return pd.DataFrame(gpd.read_file(filename))
    

def getbreakdown(filename):
    breakdwn = (dbf_to_df(filename)[['OBJECTID', 'CONTYPE', 'TOT_CNT']]
        .pivot_table(index='OBJECTID', columns='CONTYPE', values='TOT_CNT', aggfunc=np.max).fillna(0))
    breakdwn['SUM'] = breakdwn.sum(axis=1)
    breakdwn = breakdwn.divide(breakdwn['SUM'], axis=0).drop('SUM', axis=1)
    return breakdwn


# This may need conversion to crs?
def makecoords(raster):
    (xlen, ylen) = (raster.RasterXSize, raster.RasterYSize)
    (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = raster.GetGeoTransform()
    x_index = np.arange(0,xlen)
    y_index = np.arange(0,ylen)
    x_coords = x_index * x_size + upper_left_x
    y_coords = y_index * y_size + upper_left_y
    
    return x_coords, y_coords


def to_bdy(gdf):
    gdfg = gdf.geometry.unary_union   # geo df geometry
    return gpd.GeoDataFrame(geometry=[gdfg], crs=gdf.crs)


def toindx(pdser):    
    """
    going from continuous to indexed version
    take values and index them to 1-5 according to quartiles, leave 0s as is
    """
    qs = [-np.inf, 0,
          pdser[pdser>0.].quantile(0.2),
          pdser[pdser>0.].quantile(0.4),
          pdser[pdser>0.].quantile(0.6),
          pdser[pdser>0.].quantile(0.8),
          pdser[pdser>0.].quantile(1)]
    indx = [0,1,2,3,4,5]
    return pd.to_numeric(pd.cut(pdser, bins=qs, labels=indx))

"""
VOLCANO

Load and combine the volcano shp files.

pyroclastic: set to 5 if under 15km from volcano centre, 3 if 15-30km, 1 if 30-50km
lahar: set to 5 if under 50km from volcano centre, 3 if 50-100km, 1 if 100-200km
"""
def read_volcano_data(volcfile, volcnames):
    """
    Reads in the Volcano hazard data and generates hazard 'circles' around points.

    Arguments: 
        config.volcfile: name of the volcano file input data
        config.volcnames: list of strings of volcano names in the shapefile

    Returns: 
        two geopandas data frames , volcsL and volcsP, (lahar and pyroclastic)
    """
    volcs = gpd.read_file(config.volcfile)
    volcs = volcs[volcs.Volc_Name.isin(config.volcnames)]

    # Generate circles with buffer to get each radius, then take difference for each assignment
    # P - Pyroclastic
    # Indexes - get set later on - how close to volcano
    # The highest hazards are closest
    volcsP5 = to_bdy(volcs.to_crs("EPSG:32634").buffer(15000).to_crs("EPSG:4326"))  
    volcsP3 = to_bdy(volcs.to_crs("EPSG:32634").buffer(30000).to_crs("EPSG:4326"))
    volcsP1 = to_bdy(volcs.to_crs("EPSG:32634").buffer(50000).to_crs("EPSG:4326"))

    # P1 is 50km circle WITHOUT 30km circle
    volcsP1 = gpd.overlay(volcsP1, volcsP3, how='difference')  
    volcsP3 = gpd.overlay(volcsP3, volcsP5, how='difference') 

    # As above, but for lahars
    volcsL5 = to_bdy(volcs.to_crs("EPSG:32634").buffer(50000).to_crs("EPSG:4326"))
    volcsL3 = to_bdy(volcs.to_crs("EPSG:32634").buffer(100000).to_crs("EPSG:4326"))
    volcsL1 = to_bdy(volcs.to_crs("EPSG:32634").buffer(200000).to_crs("EPSG:4326"))
    # Again, we want the circles without the inner circles (so rings, effectively)
    volcsL1 = gpd.overlay(volcsL1, volcsL3, how='difference')
    volcsL3 = gpd.overlay(volcsL3, volcsL5, how='difference')


    volcsL1['lah'] = 1. #set values before combining
    volcsL3['lah'] = 3.
    volcsL5['lah'] = 5.
    volcsP1['pyr'] = 1.
    volcsP3['pyr'] = 3.
    volcsP5['pyr'] = 5.

    volcsL = volcsL1.append(volcsL3).append(volcsL5)  # combine all Lahar together
    volcsP = volcsP1.append(volcsP3).append(volcsP5) # combine pyro

    return volcsL, volcsP

"""
BUILDINGS EXPOSURE
"""
def buildings(exposure_file, exposure_breakdown_file):
    """
    Load the building data and convert to have geometry
    """
    tz_buildings = getbreakdown(config.exposure_breakdown_file)
    tz_withgeometry = dbf_to_df(config.exposure_file)

    if config.CUSTOM_VULN_CURVE:
        print("Reading vulnerabiltiy curve...")
        vuln_file = config.DATADIR + config.vuln_curve_file
        vuln_table = pd.read_csv(vuln_file, index_col=0)

        # https://stackoverflow.com/questions/52587436/find-row-closest-value-to-input
        # Extract the nearest row INDEX matching the user defined value.
        vuln_row_idx = vuln_table[vuln_table.columns[0]].sub(config.hazard_intensity).abs().idxmin()
        
        # Now retrieve that row using the lookup value INDEX
        vuln_row = vuln_table.loc[vuln_row_idx]
        
        # Now multiply the hazard vulnerablity, by building type though.
        tz_buildings= tz_buildings.mul(vuln_row, axis='columns')

    #breakpoint()
    # Multiply building percentages with set values and sum per location,
    # tz_buildings must have the building type names as columns and match the config.building_type_tz array.  
    # Combine with location id and positions to give tz.


    # Each one of these adds a new column as these don't currently exist.
    tz_buildings["plu"] = tz_buildings[config.building_type_tz].multiply(config.tz_weight_pluvial).sum(axis=1)
    tz_buildings["flu"] = tz_buildings[config.building_type_tz].multiply(config.tz_weight_fluvial).sum(axis=1)
    tz_buildings["tep"] = tz_buildings[config.building_type_tz].multiply(config.tz_weight_tephra).sum(axis=1)  #n ot currently used
    tz_buildings["lahar"] = tz_buildings[config.building_type_tz].multiply(config.tz_weight_lahar).sum(axis=1)
    tz_buildings["pyro"] = tz_buildings[config.building_type_tz].multiply(config.tz_weight_pyro).sum(axis=1)
    
    # TODO : Thought --- do we actually want another multiply here and a summation when in viln curve mode??
    if config.CUSTOM_VULN_CURVE:
        # No multiply here because we have already done it above
        tz_buildings["eq"] = tz_buildings[config.building_type_tz].sum(axis=1)
    else:
        tz_buildings["eq"] = tz_buildings[config.building_type_tz].multiply(config.tz_weight_pyro).sum(axis=1)

    # Then we drop all the other columns to just leave the hazard types. (drop obj IDs as well?)
    # Object ID still present as CONTYPE 
    tz_buildings = tz_buildings[["plu", "flu", "tep", "lahar", "pyro", "eq"]]

    # So do we want to apply the building type multiplication by vuln curve in here somewhere:
    # 1. User specifies intensity in config file
    # 2. User specifies vuln curve csv file
    # 3. Code reads in the relevant hazard risk for vuln curve type of building by lookup
    # 4. Set the risk for each CONTYPE by multiplying this value against the points in the dataframe

    # Now merge it with the Geometry set
    tz = tz_buildings.merge(
        tz_withgeometry.set_index("OBJECTID")[["geometry", "POINT_X", "POINT_Y"]], how="left", on="OBJECTID")

    """
    So at this point, we have tz which contains each hazard/risk and its assoc. point.
      and also tz_withgeometry which contains all the point data and additional geodata, plus
      the object IDs.
    """

    return tz, tz_withgeometry  # With geom gets used in the flood function later, so you need both


def flood_data(floodratio, floodtypes, tz, tz_withgeometry):
    """ 
    FLOOD DATA

    Load in flood files (tifs) and convert them to coordinates of the top corners. 
    Then assign for each location find the tif grid point that location would 
    be in to get the flood value. This can probably be done a lot better.
    """
    for i in config.floodtypes:
        print(i)
        ffile = config.DATADIR + "%s_1in%d.tif" %(i, config.floodratio)   # flood file
        print("FLOOD FILE: ", ffile)
        raster = gdal.Open(ffile)
        if config.invert_flood_tiff:
            rasterArray = raster.ReadAsArray().transpose()    # Fix transposed Nepal data
        else:
            rasterArray = raster.ReadAsArray()
        xco, yco = makecoords(raster)
        def getx(xval):
            return(np.argmax(xco[xco<xval]))
        # nb x and y values go in different directions
        def gety(yval):
            return(np.argmin(yco[yco>yval]))
        if i==config.floodtypes[0]:
            # For first flood type only - xcoA
            # doesn't have to be re run if multiple TIFFS same resolution
            xcoA, ycoA = makecoords(raster)
            xpts = tz_withgeometry.POINT_X.map(getx)
            ypts = tz_withgeometry.POINT_Y.map(gety)
        else:
            if all(xco==xcoA)==False:
                print("in x false")
                xpts = tz_withgeometry.POINT_X.map(getx)
            if all(yco==ycoA)==False:
                print("in y false")
                ypts = tz_withgeometry.POINT_Y.map(gety)
        
        # set out of range values to 0
        rasterArray[rasterArray==-9999.] = 0
        rasterArray[rasterArray==999.] = 0
        
        # Tanzania 
        # don't need building weights to work out hazard index
        tz_withgeometry = tz_withgeometry.assign(fd=rasterArray[xpts, ypts]).rename(columns={'fd':i})


        
    # convert flood values to (0) 1-5 range
    print("Converting flood values to 1-5 range...")
    for i in config.floodtypes:
        print("Converting flood type ", i)
        tz_withgeometry[i] = toindx(tz_withgeometry[i])

    print("Setting geometry index from OBJECTID")
    tz_withgeometry = tz_withgeometry.set_index("OBJECTID").merge(tz)     ## NEED to pass in tz
    print("Setting flood column from lambda function")
    tz_withgeometry = tz_withgeometry.assign(flood = lambda x: 0.5*(x.FU * x.flu + x.P * x.plu))

    # Put this in to add CRS to this dataframe if not 
    # combining with volcano data, in the original, the
    # volcano routine did this.
    gpdtz = gpd.GeoDataFrame(tz_withgeometry)
    gpdcrs = gpdtz.to_crs("EPSG:4326") 
    tz_withgeometry = gpdcrs

    return tz_withgeometry

    """
    CRS Notes

    Not sure about crs for this -  not enough info other than to use lat/lon
    Tried to put into gdf that contained boxes of the geometry - see below

    - getting x and y can be computationally expensive, so if rasters have same coords can speed up
    - Convert the flood values to an index based on the distribution of the values.
    - Out of range -9999. and 999. were set to 0 above. Values of 0 or below are not included when calculating quartiles.
    - Negative or 0 values are set to 0, values in the first quintile are set to 1, ..., values in the top quintile are set to 5.
    - Then merged into tz_withgeometry, and 'flood' set to
    - 0.5 * (fluvial building weights * fluvial index + pluvial building weights * pluvial index)
      (See to_indx() function)
    """


def combine_volcano_buildings(tz_withgeometry, volcsL, volcsP):
    """
    Combine volcano index and building weights
    """
    print("Combine volcano index and building weights")
    tz_withgeometry = gpd.sjoin(gpd.GeoDataFrame(tz_withgeometry).to_crs("EPSG:4326"), volcsL, op="within", how="left").rename(columns={'index_right':'volcsL'})
    tz_withgeometry = gpd.sjoin(tz_withgeometry, volcsP, op="within", how="left").rename(columns={'index_right':'volcsP'})

    tz_withgeometry.loc[np.isnan(tz_withgeometry.pyr), 'pyr'] = 0.
    tz_withgeometry.loc[np.isnan(tz_withgeometry.lah), 'lah'] = 0.

    print("Setting volc column from assign lamnbda function")
    tz_withgeometry = tz_withgeometry.assign(volc = lambda x: 0.45*(x.pyr * x.pyro) + 0.55*(x.lah * x.lahar))

    return tz_withgeometry


def earthquake_data(eearthquake_file):
    """
    EARTHQUAKES

    Load earthquake database, convert from points to raster grid, 
    join with tz_withgeometry to create tz_earthquakesA
    """
    print("EARTHQUAKES")
    tz_earthquakes = dbf_to_df(config.eearthquake_file)

    # tr, bl, br   - top right, bottom left/right etc
    print("Create geometry from points")
    tz_earthquakes = gpd.GeoDataFrame(
        tz_earthquakes, geometry=gpd.points_from_xy(tz_earthquakes.lon, tz_earthquakes.lat))
    tz_earthquakes = tz_earthquakes.assign(tr=tz_earthquakes.geometry.translate(xoff=0.045), bl=tz_earthquakes.geometry.translate(yoff=-0.045), br=tz_earthquakes.geometry.translate(xoff=0.045, yoff=-0.045))
    tz_earthquakes = tz_earthquakes.assign(poly=tz_earthquakes.apply(func=lambda A: Polygon([A.geometry, A.tr, A.br, A.bl]), axis=1)).drop(['geometry', 'tr', 'bl', 'br'], axis=1)

    return tz_earthquakes


def hazards_combined(tz_earthquakes, tz_withgeometry):
    # This ought to be renamed really, but we create an extra dataframe to do the work on here
    tz_earthquakesA = gpd.sjoin(tz_withgeometry, tz_earthquakes.set_geometry(col='poly', crs=tz_withgeometry.crs), op="within", how="left").rename(columns={'index_right':'tz_earthquakes'})

    # Convert PGA_0_1 to index according to quintiles as above.
    # Construct equ = (equ indx * equ building weights)
    tz_earthquakesA = tz_earthquakesA.assign(pgaindx = lambda x: toindx(x.PGA_0_1))
    tz_earthquakesA = tz_earthquakesA.rename(columns={'eq':'ear'}).assign(equ = lambda x: x.pgaindx * x.ear)

    # COMBINE
    # Combine to hazard map: 0.5*flood + 0.15 * volc + 0.35 * equ
    print("Combine all to make hmap collum")
    if config.VOLCANIC:
        tz_earthquakesA = tz_earthquakesA.assign(hmap = lambda x: 0.5*x.flood + 0.15*x.volc + 0.35*x.equ)
    else:
        # Note - we ned to think about how to reapportion ratios if skipping certain layers
        tz_earthquakesA = tz_earthquakesA.assign(hmap = lambda x: 0.5*x.flood + 0.5*x.equ)
    return tz_earthquakesA

def plot_histograms(tz_earthquakesA):
    # Plots of Histograms  -- -needs refactor----!

    plt.hist(tz_earthquakesA.equ)
    tz_earthquakesA.plot(column='equ', markersize=0.1, legend=True)
    # Stripey area - had to be rearranged first before plotting
    if config.VOLCANIC:
        plt.hist(tz_earthquakesA.volc)
        tz_earthquakesA.plot(column='volc', markersize=0.1, legend=True)
    plt.hist(tz_earthquakesA.flood)
    tz_earthquakesA.plot(column='flood', markersize=0.1, legend=True)

    if config.VOLCANIC:
        np.sum(np.isnan(tz_earthquakesA.volc))
    plt.hist(tz_earthquakesA.hmap)
    tz_earthquakesA.plot(column='hmap', markersize=0.1, legend=True)

    print(tz_earthquakesA.columns)
    tz_earthquakesA.plot(column='ear', markersize=0.01, legend=True)


def plot_maps(plots_list, figure_prefix, tz_earthquakesA):
    print("PLOTTING")
    plot = plots_list
    if plot is None:
        print("No plots requested in config. None will be drawn.")

    elif isinstance(plot, list):
        print("Plotting sequentially...")
        for plottype in plot:
            print("Printing plot: ", plottype)
            f, ax = plt.subplots(1, figsize=(8, 8))
            ax = tz_earthquakesA.plot(ax=ax, column=plottype, markersize=0.01, legend=True)
            lims = plt.axis('equal')
            plt.savefig(config.figure_prefix + plottype)

    elif isinstance(plot, str):
            print("Printing single plot: ", plot)
            f, ax = plt.subplots(1, figsize=(8, 8))
            ax = tz_earthquakesA.plot(ax=ax, column=plot, markersize=0.01, legend=True)
            lims = plt.axis('equal')
            plt.savefig(config.figure_prefix + plot)


def main():
    """The current approach is to keep updating the geopandas 
    dataframe with the extra data each function call, passing back in
    the previous geodataframe from last time, incrementally building
    up the final hazard map dataframe

    These all have side effects on the geodataframe passed in - eventually we might 
    want to refactor this to be a class with data members etc,
    """
    if config.VOLCANIC:
        volcano_lahar, volcano_pyro = read_volcano_data(config.volcfile, config.volcnames)
    tz, tz_withgeometry = buildings(config.exposure_file, config.exposure_breakdown_file)  # tz needs a rename...
    
    # Calculate earthquake data (couldn't this go above to be more logical?)
    # as above - but this one only generates earthquake data
    # if config.SEISMIC:
    tz_earthquakes = earthquake_data(config.eearthquake_file)  # as above - but this one only generates earthquake data
    # Add flood data to the buildings
    # returns tz_withgeometry again!
    tz_withgeometry_withflood = flood_data(config.floodratio, config.floodtypes, tz, tz_withgeometry)   # returns tz_withgeometry again!
    # Add volcano data to the buildingss+flood
    # as above - flood_data is the tz_geometry
    if config.VOLCANIC:
        tz_withgeometry_withflood_withvolcano = combine_volcano_buildings(tz_withgeometry_withflood, volcano_lahar, volcano_pyro)   # as above - flood_data is the tz_geometry
    else:
        tz_withgeometry_withflood_withvolcano = tz_withgeometry_withflood   # 
    # Add earthquae data to the buildings+flood+volcano data
    combined_data = hazards_combined(tz_earthquakes, tz_withgeometry_withflood_withvolcano)

    plot_histograms(combined_data)   # - this should not have side effects on the combined_data gpd
    plot_maps(config.plot_types, config.figure_prefix, combined_data)   # same as above - no side effects please!


if __name__=="__main__":
    main()