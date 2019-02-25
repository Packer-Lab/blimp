import numpy as np
import scipy
import h5py
import sys

def load_mat_struct(filename):
        """Loads MATLAB struct such that field names are made explicit as Python object structure."""
        return scipy.io.loadmat(filename, struct_as_record=False, squeeze_me=True)

def load_mat_file(filename):
    """Load using the old mat_struct load function and if this fails use the HDF5 procedure. 
    0,0,0,,0,0,0,0,0,0
    params:
        filename : the filename of the file to open
    
    returns a mat_struct for the old file format and a dictionary of dictionaries for the HDF5 format.
    """
    try: 
        mat = load_mat_struct(filename)
    except NotImplementedError:
        mat = h5py.File(filename, 'r')    
    return mat


def get_hdf5group_keys(dat):
    """ Quickly iterate over keys in HDF5 group entry and print a list of the entries. """
    keys = []
    for d in dat:
        keys.append("%s"%(d))
    return keys
