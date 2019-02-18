# blimp
interface between the pycontrol behaviour framework and PrairieView software

includes a fork of pycontrol, developed by Thomas Akam and available at: https://bitbucket.org/takam/pycontrol 

Requirements:

Python 3x, Matlab 2018b or later

Currently does not work with python versions later than 3.6

The matlab engine must be compiled for use.

To do this cd as admin to matlabroot/extern/engines/python and run: 'python setup.py install'

matlabroot can be found by entering matlabroot into matlab command line.

Add blimp recursively to the matlab path in startup.m using addpath(genpath(path/to/blimp/)) 
