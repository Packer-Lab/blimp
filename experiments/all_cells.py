import matlab.engine
import yaml
import os
import time
import random
import numpy as np
from threading import Thread, active_count
import tifffile
import imageio
import asyncio
from utils.utils_funcs import load_mat_file
import multiprocessing
import matlab.engine
from multiprocessing import Process
from concurrent.futures import ProcessPoolExecutor
import concurrent
from distutils.dir_util import copy_tree
from multiprocessing import Pool


class AllCells():

    def __init__(self, Blimp):

        self._blimp = Blimp

        if self._blimp.yaml_dict['redo_naparm']:
            _points_obj = self._blimp.eng.Main(self._blimp.naparm_path, 'processAll', 1, 'GroupSize', self._blimp.group_size, 'SavePath', self._blimp.output_folder)
            self.all_points = _points_obj['all_points']

        else:
            _points_path = next(os.path.join(self._blimp.naparm_path,file) for file in os.listdir(self._blimp.naparm_path) if file.endswith('_Points.mat'))
            self.all_points = load_mat_file(_points_path)['points']
            #copy the phase masks
            copy_tree(os.path.join(self._blimp.naparm_path, 'PhaseMasks'), os.path.join(self._blimp.output_folder, 'PhaseMasks'))
            #copy the whole naparm directory in case of future issues
            copy_tree(self._blimp.naparm_path, os.path.join(self._blimp.output_folder, 'naparm'))


        # into foxy ratio format
        galvo_x = np.asarray(self.all_points['centroid_x']).squeeze() / 512
        galvo_y = np.asarray(self.all_points['centroid_y']).squeeze() / 512

        assert len(galvo_x) == len(galvo_y)

        num_groups = len(galvo_x)

        group_list = []

        mW_power = self._blimp.group_size * self._blimp.mWperCell
        print('group size is {}'.format(self._blimp.group_size))
        print('mw power is {}'.format(mW_power))

        pv_power = self._blimp.mw2pv(mW_power)
        print('PV power is {}'.format(pv_power))
        
        
        

        for group in range(num_groups):
            # string for each group is nested in list for each percent
            group_string = self._blimp.build_strings (X = galvo_x[group], Y = galvo_y[group], \
                                                    duration = self._blimp.duration, laser_power = pv_power, \
                                                    is_spiral = 'true', spiral_revolutions = self._blimp.spiral_revolutions, \
                                                    spiral_size = self._blimp.spiral_size, num_spirals = self._blimp.num_spirals)

            group_list.append(group_string)

        #merge each group into a single string
        self.all_groups_mp = self._blimp.groups_strings(self._blimp.inter_group_interval, group_list, SLM_trigger = True, n_repeats=self._blimp.num_repeats)


        #init numpy arrays from tiffs
        mask_path = os.path.join(self._blimp.output_folder, 'PhaseMasks')
        tiff_list = [os.path.join(mask_path,file) for file in os.listdir(mask_path) if file.endswith('.tiff') or file.endswith('.tif')]
        self.mask_list = [tifffile.imread(tiff) for tiff in tiff_list]

        print('{} Phase mask tiffs found'.format(len(tiff_list)))

        #arrays of precaculated frame locations in memory
        self.repeat_arrays = self._blimp.sdk.precalculate_masks(self.mask_list, num_repeats=self._blimp.num_repeats)


    def slm_trial(self):

        ##the threaded function
        slm_thread = Thread(target=self._blimp.sdk.load_precalculated_triggered, args = [self.repeat_arrays])
        slm_thread.start()


        time.sleep(0.01)

        # this function laods the 15ms trigger sequences to the hardware and begins the sequence
        self.mp_output = self._blimp.prairie.pl.SendScriptCommands(self.all_groups_mp)
        self._blimp.write_output(self._blimp.trial_runtime, self._blimp.trial_number, self._blimp.barcode, 'all_cells_stimulated')


    def nogo_trial(self):
            ''' called when an nogo  trial is initiated '''
            # #change the uncaging power in the string to 0
            _space_split = self.all_groups_mp.split(' ')
            power_idx= [idx+1 for idx, el in enumerate(_space_split) if el == 'Uncaging']

            for idx in power_idx:
                _space_split[idx] = '0'
            
            _nogo_trial_string = (' ').join(_space_split)

            self._blimp.write_output(self._blimp.trial_runtime, self._blimp.trial_number, self._blimp.barcode, 'all_cells_nogo')

            # this function laods the 15ms trigger sequences to the hardware and begins the sequence
            self.mp_output = self._blimp.prairie.pl.SendScriptCommands(_nogo_trial_string)