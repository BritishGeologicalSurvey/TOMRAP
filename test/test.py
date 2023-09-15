import os
import pytest
import logging

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.testing.decorators import image_comparison

from hazardmaps import hazardmap as hazmap
from hazardmaps.config import volcfile, volcnames, exposure_file, exposure_breakdown_file, floodratio, floodtypes, earthquake_file

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


@pytest.mark.mpl_image_compare
def test_succeeds():
    """
    Very simple test to check that the matplotlib
    image compare hook is set up correctly.
    """
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,3], linestyle='-')
    return fig


@pytest.mark.skipif(os.getenv("GITLAB_CI") is not None, reason="cannot run this test on CI server due to data requirement")
@pytest.mark.mpl_image_compare
def test_hazard_map_regression():
    """Regression test to check that running a full hazard map analysis to completion
    produces the same map by the way of an image comparison check. 
    
    You must run this test locally. If the test case data is changed, you will need
    to regenerate the test images, the "baseline" images.  and replace
    the ones in the baseline folder in the test directory. 
    
    pytest --mpl-generate-path="test/baseline" test/test.py
    
    Then run the tests with the --mpl flag
    
    pytest --mpl test/test.py
    """
    logging.info("Generating regression test data...this may take a while")
    # The steps below are similar to the ones found in the main() function in the hazardmaps.py file
    volcano_lahar, volcano_pyro = hazmap.read_volcano_data(volcfile, volcnames)
    tz, tz_withgeometry = hazmap.buildings(exposure_file, exposure_breakdown_file)
    tz_withgeometry_withflood = hazmap.flood_data(floodratio, floodtypes, tz, tz_withgeometry)
    tz_withgeometry_withflood_withvolcano = hazmap.combine_volcano_buildings(tz_withgeometry_withflood, volcano_lahar, volcano_pyro)
    tz_earthquakes = hazmap.earthquake_data(earthquake_file)  
    combined_data = hazmap.hazards_combined(tz_earthquakes, tz_withgeometry_withflood_withvolcano)
    np.sum(np.isnan(combined_data.volc))

    logging.info("Printing single hmap plot:")

    # Now plot the test figures
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax = combined_data.plot(ax=ax, column="hmap", markersize=0.01, legend=True)  

    lims = plt.axis('equal')
    # Test function must return the figure to work with the mpl image compare decorator
    return fig   
