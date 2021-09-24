import os
import pytest
import numpy as np
import matplotlib.pyplot as plt
import hazardmap as hazmap

from config import volcfile, volcnames, exposure_file, exposure_breakdown_file, floodratio, floodtypes, eearthquake_file


@pytest.mark.mpl_image_compare
def test_succeeds():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,3], linestyle='-')
    return fig

# This is a long-running test as it essential runs the whole script against
# the full Tanzania dataset.
@pytest.mark.skipif(os.getenv(["GITLAB_CI"]) is not None, reason="cannot run this test on CI server due to data requirement")
@pytest.mark.mpl_image_compare
def test_hazard_map_regression():
    # Call the main function here to get the image gpd
    print("Generating regression test data...this may take a while")
    volcano_lahar, volcano_pyro = hazmap.read_volcano_data(volcfile, volcnames)
    tz, tz_withgeometry = hazmap.buildings(exposure_file, exposure_breakdown_file)  # tz needs a rename...
    tz_withgeometry_withflood = hazmap.flood_data(floodratio, floodtypes, tz, tz_withgeometry)   # returns tz_withgeometry again!
    tz_withgeometry_withflood_withvolcano = hazmap.combine_volcano_buildings(tz_withgeometry_withflood, volcano_lahar, volcano_pyro)   # as above - flood_data is the tz_geometry
    tz_earthquakes = hazmap.earthquake_data(eearthquake_file)  # as above - but this one only generates earthquake data
    combined_data = hazmap.hazards_combined(tz_earthquakes, tz_withgeometry_withflood_withvolcano)

    np.sum(np.isnan(combined_data.volc))

    print("Printing single hmap plot:")

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax = combined_data.plot(ax=ax, column="hmap", markersize=0.01, legend=True)   # Problemm calling from pandas?
    plt.savefig("regression_test_hmap_step1.png")
    lims = plt.axis('equal')
    plt.savefig("regression_test_hmap_step2.png")
    return fig  # Test function must return the figure to work wth decorator
