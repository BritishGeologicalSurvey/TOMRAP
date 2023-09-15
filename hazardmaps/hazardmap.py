import logging

import pandas as pd
import numpy as np
import geopandas as gpd
from osgeo import gdal
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

import hazardmaps.config as config

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def get_dataframe(filename):
    """
    Read in a dbf file (database format by ESRI)
    and return it as a pandas DataFrame

    Args:
        filename (Path or str): DBF file

    Returns:
        pd.DataFrame: dataframe cotaiing the DBF file
    """
    logging.info("LOADING FILE %s", filename)
    return pd.DataFrame(gpd.read_file(filename))
    

def get_breakdown_dataframe(filename):
    """
    Function to read in a building-type DBF database, this is slightly more complex
    than a standard dbf file, and requires a separate function to process the table and
    return a pivot table of the building types for hazard analyses.

    Args:
        filename (Path or str): Filename for buildings 

    Returns:
        pd.DataFrame: pandas dataframe
    """
    breakdown = (get_dataframe(filename)[['OBJECTID', 'CONTYPE', 'TOT_CNT']]
        .pivot_table(index='OBJECTID', columns='CONTYPE', values='TOT_CNT', aggfunc=np.max).fillna(0))
    breakdown['SUM'] = breakdown.sum(axis=1)
    breakdown = breakdown.divide(breakdown['SUM'], axis=0).drop('SUM', axis=1)
    return breakdown


def make_coords(raster):
    """
    Return an array of x and y coordinates from a given raster

    Args:
        raster (gdal raster): GDAL Raster object

    Returns:
        np.array: x coordinates, y_coordinates
    """
    (xlen, ylen) = (raster.RasterXSize, raster.RasterYSize)
    (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = raster.GetGeoTransform()
    x_index = np.arange(0,xlen)
    y_index = np.arange(0,ylen)
    x_coords = x_index * x_size + upper_left_x
    y_coords = y_index * y_size + upper_left_y
    
    return x_coords, y_coords


def to_boundary(gdf):
    """
    Generate "buffer circles" for deteriming the extent of each hazard.

    Args:
        gdf (GeoPandas DataFrame): Input dataframe with hazard features.

    Returns:
        Geopandas DataFrame: the geodataframe containing a unary union of all the geometries.
    """
    gdfg = gdf.geometry.unary_union
    return gpd.GeoDataFrame(geometry=[gdfg], crs=gdf.crs)


def to_index(pdser):    
    """
    Takes the input series from continuous to indexed version
    Uses values and indexes them to 1-5 according to quantiles, leaves 0s as is
    
    Args:
        pdser: pd.Series
        
    Returns:
        pd.Series: classified series with bins according to quantile indices.
    """
    quantiles = [-np.inf, 0,
          pdser[pdser>0.].quantile(0.2),
          pdser[pdser>0.].quantile(0.4),
          pdser[pdser>0.].quantile(0.6),
          pdser[pdser>0.].quantile(0.8),
          pdser[pdser>0.].quantile(1)]
    indx = [0,1,2,3,4,5]
    return pd.to_numeric(pd.cut(pdser, bins=quantiles, labels=indx))


def read_volcano_data(volcfile, volcnames):
    """
    Reads in the Volcano hazard data and generates hazard 'circles' around points.

    Args: 
        config.volcfile: name of the volcano file input data
        config.volcnames: list of strings of volcano names in the shapefile

    Returns: 
        Two geopandas data frames, volcsL and volcsP, (Lahar and Pyroclastic hazards)
    """
    volcs = gpd.read_file(volcfile)
    volcs = volcs[volcs.Volc_Name.isin(volcnames)]

    # Generate circles with buffer to get each radius, then take difference for each assignment
    # P - Pyroclastic
    # The highest risk hazards are closest
    volcsP5 = to_boundary(volcs.to_crs("EPSG:32634").buffer(15000).to_crs("EPSG:4326"))  
    volcsP3 = to_boundary(volcs.to_crs("EPSG:32634").buffer(30000).to_crs("EPSG:4326"))
    volcsP1 = to_boundary(volcs.to_crs("EPSG:32634").buffer(50000).to_crs("EPSG:4326"))

    # P1 is 50km circle WITHOUT 30km circle
    volcsP1 = gpd.overlay(volcsP1, volcsP3, how='difference')  
    volcsP3 = gpd.overlay(volcsP3, volcsP5, how='difference') 

    # L - Lahars
    # As above, but for lahars
    volcsL5 = to_boundary(volcs.to_crs("EPSG:32634").buffer(50000).to_crs("EPSG:4326"))
    volcsL3 = to_boundary(volcs.to_crs("EPSG:32634").buffer(100000).to_crs("EPSG:4326"))
    volcsL1 = to_boundary(volcs.to_crs("EPSG:32634").buffer(200000).to_crs("EPSG:4326"))
    # Again, we want the circles without the inner circles (so rings, effectively)
    volcsL1 = gpd.overlay(volcsL1, volcsL3, how='difference')
    volcsL3 = gpd.overlay(volcsL3, volcsL5, how='difference')

    """
    Pyroclastic: set to 5 if under 15km from volcano centre, 3 if 15-30km, 1 if 30-50km
    Lahar: set to 5 if under 50km from volcano centre, 3 if 50-100km, 1 if 100-200km
    """
    volcsL1['lah'] = 1. 
    volcsL3['lah'] = 3.
    volcsL5['lah'] = 5.
    volcsP1['pyr'] = 1.
    volcsP3['pyr'] = 3.
    volcsP5['pyr'] = 5.

    volcsL = volcsL1.append(volcsL3).append(volcsL5)  # combine all lahar hazards
    volcsP = volcsP1.append(volcsP3).append(volcsP5)  # combine pyroclastic hazards

    return volcsL, volcsP


def buildings(exposure_file, exposure_breakdown_file):
    """
    Load the building data and convert to have geometry
    """
    logging.info("Getting breakdown file from DBF %s...(This may take a while...)", exposure_breakdown_file)
    tz_buildings = get_breakdown_dataframe(exposure_breakdown_file)
    logging.info("Loading full Building Exposire File from %s. (This may take a while....)", exposure_file)
    tz_withgeometry = get_dataframe(exposure_file)

    if config.CUSTOM_VULN_CURVE:
        logging.info("Reading vulnerabiltiy curve...")
        vuln_file = config.DATADIR + config.vuln_curve_file
        vuln_table = pd.read_csv(vuln_file, index_col=0)

        # https://stackoverflow.com/questions/52587436/find-row-closest-value-to-input
        # Extract the nearest row INDEX matching the user defined value.
        vuln_row_idx = vuln_table[vuln_table.columns[0]].sub(config.hazard_intensity).abs().idxmin()
        
        # Now retrieve that row using the lookup value INDEX
        vuln_row = vuln_table.loc[vuln_row_idx]
        
        # Now multiply the hazard vulnerablity, by building type though.
        tz_buildings= tz_buildings.mul(vuln_row, axis='columns')

    """
    Multiply building percentages with set values and sum per location,
    tz_buildings must have the building type names as columns and match the config.building_type_tz array.  
    Combine with location id and positions to give tz.
    Each one of these adds a new column as these don't currently exist.
    """
    tz_buildings["plu"] = tz_buildings[config.building_type_tz].multiply(config.tz_weight_pluvial).sum(axis=1)
    tz_buildings["flu"] = tz_buildings[config.building_type_tz].multiply(config.tz_weight_fluvial).sum(axis=1)
    tz_buildings["tep"] = tz_buildings[config.building_type_tz].multiply(config.tz_weight_tephra).sum(axis=1)  #n ot currently used
    tz_buildings["lahar"] = tz_buildings[config.building_type_tz].multiply(config.tz_weight_lahar).sum(axis=1)
    tz_buildings["pyro"] = tz_buildings[config.building_type_tz].multiply(config.tz_weight_pyro).sum(axis=1)
    
    if config.CUSTOM_VULN_CURVE:
        # No multiply here because we have already done it above
        tz_buildings["eq"] = tz_buildings[config.building_type_tz].sum(axis=1)
    else:
        tz_buildings["eq"] = tz_buildings[config.building_type_tz].multiply(config.tz_weight_pyro).sum(axis=1)

    # Then we drop all the other columns to just leave the hazard types
    tz_buildings = tz_buildings[["plu", "flu", "tep", "lahar", "pyro", "eq"]]

    # Now merge it with the Geometry set
    tz = tz_buildings.merge(
        tz_withgeometry.set_index("OBJECTID")[["geometry", "POINT_X", "POINT_Y"]], how="left", on="OBJECTID")

    """
    So at this point, we have "tz" which contains each hazard/risk and its assoc. point.
      and also "tz_withgeometry" which contains all the point data and additional geodata, plus
      the object IDs.
    """
    return tz, tz_withgeometry  # With geom gets used in the flood function later, so you need both


def flood_data(floodratio, floodtypes, tz, tz_withgeometry):
    """ 
    FLOOD HAZARDS

    Load in flood files (tifs) and convert them to coordinates of the top corners. 
    Then assign for each location find the tif grid point that location would 
    be in to get the flood value. This can probably be done a lot better.
    
    Args: 
        floodratio: int (1 in 100 yr, 1 in 200 year flood etc)   (set in config file)
        floodtypes: [list of str]  fluvial, pluvial, etc         (set in config file)  
        tz:  Geopandas dataframe
        tz_withgeometry:  Geopandas dataframe with geometry
    
    Returns:
        tz_withgeometry (as above but updated with the flood risk)
    """
    for i in floodtypes:
        ffile = config.DATADIR + "%s_1in%d.tif" %(i, floodratio)
        logging.info("FLOOD FILE: %s, 1 in %s", ffile, i)
        raster = gdal.Open(ffile)
        if config.invert_flood_tiff:
            rasterArray = raster.ReadAsArray().transpose()
        else:
            rasterArray = raster.ReadAsArray()
        xco, yco = make_coords(raster)
        
        # Helper functions
        def getx(xval):
            return(np.argmax(xco[xco < xval]))
        # nb x and y values go in different directions
        def gety(yval):
            return(np.argmin(yco[yco > yval]))
        
        if i==config.floodtypes[0]:
            # For first flood type only - xcoA
            # doesn't have to be re run if multiple TIFFS same resolution
            xcoA, ycoA = make_coords(raster)
            xpts = tz_withgeometry.POINT_X.map(getx)
            ypts = tz_withgeometry.POINT_Y.map(gety)
        else:
            if all(xco==xcoA)==False:
                logging.info("in x false")
                xpts = tz_withgeometry.POINT_X.map(getx)
            if all(yco==ycoA)==False:
                logging.info("in y false")
                ypts = tz_withgeometry.POINT_Y.map(gety)
        
        # Set out of range values to 0
        rasterArray[rasterArray==-9999.] = 0
        rasterArray[rasterArray==999.] = 0
        
        tz_withgeometry = tz_withgeometry.assign(fd=rasterArray[xpts, ypts]).rename(columns={'fd':i})

    # Convert flood values to (0) 1-5 range
    logging.info("Converting flood values to 1-5 range...")
    for i in config.floodtypes:
        logging.info("Converting flood type %s", i)
        tz_withgeometry[i] = to_index(tz_withgeometry[i])

    logging.info("Setting geometry index from OBJECTID")
    tz_withgeometry = tz_withgeometry.set_index("OBJECTID").merge(tz)     ## NEED to pass in tz
    logging.info("Setting flood column from lambda function")
    tz_withgeometry = tz_withgeometry.assign(flood = lambda x: 0.5*(x.FU * x.flu + x.P * x.plu))

    # Put this in to add CRS to this dataframe if not 
    # combining with volcano data, in the original, the
    # volcano routine did this.
    gpdtz = gpd.GeoDataFrame(tz_withgeometry)
    gpdcrs = gpdtz.to_crs("EPSG:4326") 
    tz_withgeometry = gpdcrs

    return tz_withgeometry


def combine_volcano_buildings(tz_withgeometry, volcsL, volcsP):
    """
    Combine volcano index and building weights
    
    Args:
        tz_withgeometry: Pandas Geodataframe
        volcsL: Pandas Geodataframe with Lahar data
        volcsP: Pandas Geodataframe with Pyroclastic data
    
    Returns:
        tz_withgeometry: Pandas Geodataframe updated with volcanic hazard.
    """
    logging.info("Combine volcano index and building weights")
    tz_withgeometry = gpd.sjoin(gpd.GeoDataFrame(tz_withgeometry).to_crs("EPSG:4326"), volcsL, op="within", how="left").rename(columns={'index_right':'volcsL'})
    tz_withgeometry = gpd.sjoin(tz_withgeometry, volcsP, op="within", how="left").rename(columns={'index_right':'volcsP'})

    tz_withgeometry.loc[np.isnan(tz_withgeometry.pyr), 'pyr'] = 0.
    tz_withgeometry.loc[np.isnan(tz_withgeometry.lah), 'lah'] = 0.

    logging.info("Setting volc column from assign lamnbda function")
    tz_withgeometry = tz_withgeometry.assign(volc = lambda x: 0.45*(x.pyr * x.pyro) + 0.55*(x.lah * x.lahar))

    return tz_withgeometry


def earthquake_data(earthquake_file):
    """
    EARTHQUAKES

    Load earthquake database, convert from points to raster grid, 
    join with tz_withgeometry to create tz_earthquakesA
    
    Args:
        earthquake_file: (Path or str)  georeferenced earthquake database file
    
    Returns:
        tz_earthquakes: (Geopandas Dataframe)   
    """
    logging.info("Calculating earthquake hazard")
    tz_earthquakes = get_dataframe(earthquake_file)

    # tr, bl, br - top right, bottom left/right etc.
    logging.info("Create geometry from points")
    tz_earthquakes = gpd.GeoDataFrame(
        tz_earthquakes, geometry=gpd.points_from_xy(tz_earthquakes.lon, tz_earthquakes.lat))
    
    tz_earthquakes = tz_earthquakes.assign(tr=tz_earthquakes.geometry.translate(xoff=0.045),
                                           bl=tz_earthquakes.geometry.translate(yoff=-0.045),
                                           br=tz_earthquakes.geometry.translate(xoff=0.045, yoff=-0.045))
    tz_earthquakes = tz_earthquakes.assign(poly=tz_earthquakes.apply(
        func=lambda A: Polygon([A.geometry, A.tr, A.br, A.bl]), axis=1)).drop(['geometry', 'tr', 'bl', 'br'], axis=1)

    return tz_earthquakes


def hazards_combined(tz_earthquakes, tz_withgeometry):
    """
    Combine all hazards with any earthquake datasets present.

    Args:
        tz_earthquakes (Geopandas Dataframe): Earthquakes 
        tz_withgeometry (Geopandas Dataframe): Other Hazards (already combined)

    Returns:
        tz_earthquakesA: Geopandas Dataframe with all combined hazards present.
    """
    # We create a temporary extra dataframe to do the work on here
    tz_earthquakesA = gpd.sjoin(tz_withgeometry, 
                                tz_earthquakes.set_geometry(col='poly', crs=tz_withgeometry.crs),
                                                            op="within", how="left").rename(columns={'index_right':'tz_earthquakes'})

    # Convert PGA_0_1 to index according to quintiles as above.
    # Construct equ = (equ indx * equ building weights)
    tz_earthquakesA = tz_earthquakesA.assign(pgaindx = lambda x: to_index(x.PGA_0_1))
    tz_earthquakesA = tz_earthquakesA.rename(columns={'eq':'ear'}).assign(equ = lambda x: x.pgaindx * x.ear)

    # Combine to hazard map: 0.5 * flood + 0.15 * volc + 0.35 * equ
    logging.info("Combine all to make hmap collum")
    if config.VOLCANIC:
        tz_earthquakesA = tz_earthquakesA.assign(hmap = lambda x: 0.5*x.flood + 0.15*x.volc + 0.35*x.equ)
    else:
        # Note - we ned to think about how to reapportion ratios if skipping certain layers
        tz_earthquakesA = tz_earthquakesA.assign(hmap = lambda x: 0.5*x.flood + 0.5*x.equ)
    return tz_earthquakesA


def plot_histograms(tz_earthquakesA):
    """Plot histogram plots

    Args:
        tz_earthquakesA (Geopandas Dataframe): Combined Hazard Dataframe
    """
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

    logging.info("Plotting histogram %s", tz_earthquakesA.columns)
    tz_earthquakesA.plot(column='ear', markersize=0.01, legend=True)


def plot_maps(plots_list, figure_prefix, tz_earthquakesA):
    """Plot hazard maps

    Args:
        plots_list (List): List of plot type codes set in config
        figure_prefix (str): Prefix the figure files with this string
        tz_earthquakesA (Geopandas Dataframe): Final Comabined Hazards Geodataframe
    """
    logging.info("PLOTTING")
    plot = plots_list
    if plot is None:
        logging.info("No plots requested in config. None will be drawn.")

    elif isinstance(plot, list):
        logging.info("Plotting sequentially...")
        for plottype in plot:
            logging.info("Printing plot: ", plottype)
            f, ax = plt.subplots(1, figsize=(8, 8))
            ax = tz_earthquakesA.plot(ax=ax, column=plottype, markersize=0.01, legend=True)
            lims = plt.axis('equal')
            plt.savefig(config.figure_prefix + plottype)

    elif isinstance(plot, str):
            logging.info("Printing single plot: ", plot)
            f, ax = plt.subplots(1, figsize=(8, 8))
            ax = tz_earthquakesA.plot(ax=ax, column=plot, markersize=0.01, legend=True)
            lims = plt.axis('equal')
            plt.savefig(config.figure_prefix + plot)


def main():
    """
    The current approach is to keep updating the geopandas 
    dataframe with the extra data each function call, passing back in
    the previous geodataframe from last time, incrementally building
    up the final hazard map dataframe from each added hazard.

    These all have side effects on the geodataframe passed in - eventually we might 
    want to refactor this to be a class with data members etc. But that is for a future release.
    """
    logging.info("WELCOME TO TOMRAP: Toolbox for Multihazard Risk Assessment in Python")
    if config.VOLCANIC:
        logging.info("Reading volcanic hazard inputs...")
        volcano_lahar, volcano_pyro = read_volcano_data(config.volcfile, config.volcnames)
        logging.info("SUCCESS: Reading volcanic hazard inputs")
        
    logging.info("Extracting building geometry and exposure database...")
    tz, tz_withgeometry = buildings(config.exposure_file, config.exposure_breakdown_file)  # tz needs a rename...
    logging.info("SUCCESS: Extracting building geometry and exposure database.")
    
    # Calculate earthquake data (couldn't this go above to be more logical?)
    # as above - but this one only generates earthquake data
    logging.info("Reading Earthquake (Seismic) data...")
    tz_earthquakes = earthquake_data(config.earthquake_file)  # as above - but this one only generates earthquake data
    # Add flood data to the buildings
    # returns tz_withgeometry again!
    logging.info("Combining flood and building geometry data...")
    tz_withgeometry_withflood = flood_data(config.floodratio, config.floodtypes, tz, tz_withgeometry)  
    # Add volcano data to the buildingss+flood
    # as above - flood_data is the tz_geometry
    if config.VOLCANIC:
        logging.info("Combining volcanic and building geometry data...")
        tz_withgeometry_withflood_withvolcano = combine_volcano_buildings(tz_withgeometry_withflood, volcano_lahar, volcano_pyro)   # as above - flood_data is the tz_geometry
    else:
        tz_withgeometry_withflood_withvolcano = tz_withgeometry_withflood 
    # Add earthquae data to the buildings+flood+volcano data
    logging.info("Combining all data to map")
    combined_data = hazards_combined(tz_earthquakes, tz_withgeometry_withflood_withvolcano)

    logging.info("Plotting histograms")
    plot_histograms(combined_data)
    logging.info("Plotting maps")
    plot_maps(config.plot_types, config.figure_prefix, combined_data)
    logging.info("FINISHED.")


if __name__=="__main__":
    main()