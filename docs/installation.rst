
Installation Requirements
=========================

This repository should be cloned to your local machine. The software depends on some 3rd Party Python 
libraries to run. The easiest way to manage the installation of these is using a conda environment.
The list of required packages is given in environment.yml.

General Instructions
--------------------

You must have a Python installation to run the software. I recommend using the Anaconda distribution as
it is aimed at scientific users of Python, and provides a *package manager* called Conda which makes
installation a bit easier. 

In Conda terminology, we talk about having an "environment" which contains all the libraries and
other packages required to run the software. This helps to stop the software libraries conflicting
with other packages already installed on your system.

There are two files provided which can create your Conda environment, one for Linux systems and one
for Windows systems.

 * `environment_linux.yml`
 * `environment_windows.yml`

In the instructions below, substitute the `environment.yml` file with the one for your system.

To create a conda environment once you have an installation of conda installed, you can run:

.. code-block:: bash

	conda env create -f environment.yml --name hazmaps
	conda activate hazmaps


After using the software/script, you can deactivate this environment with

.. code-block:: bash

	conda deactivate


BGS Specififc Instructions and Installtion Troubleshooting
-----------------------------------------------------------

BGS users will most likely be using a Windows environment, this should ideally be provided 
by using the "Company Portal" to install the Anaconda distribution. Then, create your conda 
environment either by using the Anaconda Navigator GUI, or use the Anaconda Powershell Prompt 
to run the command line set up above.

Remember each time you want to use TOMRAP, you must activate the `hazmaps` conda environment you created
in the steps above. Either using the command line, or via Anaconda Navigator. 








