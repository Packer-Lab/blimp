import numpy as np
import scipy.io as sio
import h5py
import sys

def threshold_detect(signal, threshold):
    thresh_signal = signal > threshold
    thresh_signal[1:][thresh_signal[:-1] & thresh_signal[1:]] = False
    times = np.where(thresh_signal)
    return times[0]
    
def load_mat_struct(filename):
        """Loads MATLAB struct such that field names are made explicit as Python object structure."""
        return sio.loadmat(filename, struct_as_record=True, squeeze_me=True)

def load_mat_file(filename):
    """Load using the old mat_struct load function and if this fails use the HDF5 procedure. 
    0,0,0,,0,0,0,0,0,0
    params:
        filename : the filename of the file to open
    
    returns a mat_struct for the old file format and a dictionary of dictionaries for the HDF5 format.
    """
    try: 
        mat = load_mat_struct(filename)
    except:
        mat = h5py.File(filename, 'r')    
    return mat


def get_hdf5group_keys(dat):
    """ Quickly iterate over keys in HDF5 group entry and print a list of the entries. """
    keys = []
    for d in dat:
        keys.append("%s"%(d))
    return keys
    

def tangent(x, phi, I_0, I, k):
    '''takes *popt from power measurements and returns inverse of matthias arctan func'''
    return (np.tan((x - I_0) / I) / k) - phi