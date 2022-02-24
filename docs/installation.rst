
Installation Requirements
=========================

This repository should be cloned to your local machine. The software depends on some 3rd Party Python 
libraries to run. The easiest way to manage the installation of these is using a conda environment.
The list of required packages is given in environment.yml.

To create a conda environment once you have an installation of conda installed, you can run:

.. code-block:: bash

	conda create -f environment.yml --name hazmap
	conda activate hazmap


After using the software/script, you can deactivate this environment with

.. code-block:: bash

	conda deactivate
