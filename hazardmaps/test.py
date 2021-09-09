import pytest
import matplotlib.pyplot as plt

@pytest.mark.mpl_image_compare
def test_succeeds():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,3], linestyle='-')
    return fig


"""
To run the full test suite, you need to run the data ingest 
script, and then call the plot_() function on the images
you want to check (it will take a while)
"""