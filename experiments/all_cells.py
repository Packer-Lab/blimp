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
    
        self.Blimp = Blimp
        
        if self.Blimp.yaml_dict['redo_naparm']:
            _points_obj = self.Blimp.eng.Main(self.Blimp.naparm_path, 'processAll', 1, 'GroupSize', self.Blimp.group_size, 'SavePath', self.Blimp.output_folder)
            self.all_points = _points_obj['all_points']

        else:
            _points_path = next(os.path.join(self.Blimp.naparm_path,file) for file in os.listdir(self.Blimp.naparm_path) if file.endswith('_Points.mat'))
            self.all_points = load_mat_file(_points_path)['points']
            #copy the phase masks
            copy_tree(os.path.join(self.Blimp.naparm_path, 'PhaseMasks'), os.path.join(self.Blimp.output_folder, 'PhaseMasks'))
            #copy the whole naparm directory in case of future issues
            copy_tree(self.Blimp.naparm_path, os.path.join(self.Blimp.output_folder, 'naparm'))

 
        # into foxy ratio format
        galvo_x = np.asarray(all_points['centroid_x']).squeeze() / 512
        galvo_y = np.asarray(all_points['centroid_y']).squeeze() / 512

        assert len(galvo_x) == len(galvo_y)
        
        num_groups = len(galvo_x)
        
        group_list = []        
        
        for group in range(num_groups):
                
            #the shape of the point array shows the group size
            group_size = np.asarray(all_points['points_array'][group]).shape[0]
            
            mW_power = group_size * self.Blimp.mWperCell  
            print('group size is {}'.format(group_size))
            print('mw per cells is {}'.format(self.Blimp.mWperCell))
            
            pv_power = self.Blimp.eng.mw2pv(mW_power)
            #print('PV power is {}'.format(pv_power))
           
            
            # string for each group is nested in list for each percent
            group_string = self.Blimp.build_strings (X = galvo_x[group], Y = galvo_y[group], \
                                                    duration = self.Blimp.duration, laser_power = pv_power, \
                                                    is_spiral = 'true', spiral_revolutions = self.Blimp.spiral_revolutions, \
                                                    spiral_size = self.Blimp.spiral_size, num_spirals = self.Blimp.num_spirals)   
                                                                 
            group_list.append(group_string)
                
        #merge each group into a single string
        self.all_groups_mp = self.Blimp.groups_strings(self.Blimp.inter_group_interval, group_list, SLM_trigger = True, n_repeats=self.Blimp.num_repeats)
        
        
        #init numpy arrays from tiffs
        mask_path = os.path.join(self.Blimp.output_folder, 'PhaseMasks')
        tiff_list = [os.path.join(mask_path,file) for file in os.listdir(mask_path) if file.endswith('.tiff') or file.endswith('.tif')]
        self.mask_list = [tifffile.imread(tiff) for tiff in tiff_list]
 
        print('{} Phase mask tiffs found'.format(len(tiff_list)))
        
        #arrays of precaculated frame locations in memory
        self.repeat_arrays = self.Blimp.precalculate_masks(self.mask_list, num_repeats=self.Blimp.num_repeats)
        
        
    def run_experiment(self):  
        
        ##the threaded function
        slm_thread = Thread(target=self.Blimp.load_precalculated_triggered, args = [self.repeat_arrays])
        slm_thread.start()


        time.sleep(0.01)
        
        # this function laods the 15ms trigger sequences to the hardware and begins the sequence 
        self.mp_output = self.Blimp.pl.SendScriptCommands(self.all_groups_mp)
        self.Blimp.write_output(self.Blimp.trial_runtime, self.Blimp.trial_number, self.Blimp.barcode, 'all_cells_stimulated')
        

        
        

                        
def unwrap_self_f(arg, **kwarg):
    
    return AllCells.Blimp.load_precalculated_triggered(*arg, **kwarg)
        
        
        


            
