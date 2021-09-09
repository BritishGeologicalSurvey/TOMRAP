import pytest
#from matplotlib.testing.conftest import mpl_test_settings
import matplotlib.pyplot as plt
#from matplotlib.testing.decorators import image_comparison

plt.close('all')

import pytest
import matplotlib.pyplot as plt

@pytest.mark.mpl_image_compare
def test_succeeds():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax = fig.add_subplot(2,1,1)
    ax.plot([1,2,5], linestyle='--')
    return fig
"""
## Example stub of testing - put in separate file
@image_comparison(baseline_images=['line_dashes'], remove_text=True,
                  extensions=['png'])
def test_line_dashes():
    fig, ax = plt.subplots()
    ax.plot(range(10), linestyle=(0, (3, 3)), lw=5)

plt.close('all')

@image_comparison(baseline_images=['small_dashes'], remove_text=True,
                  extensions=['png'])
def test_small_dash():
    fig, ax = plt.subplots()
    ax.plot(range(10), linestyle=(0, (1, 1)), lw=1)
"""