import matlab.engine
import yaml
import os
import time
import random
import numpy as np
from threading import Thread
import tifffile
import imageio

class AllCells():

    def __init__(self, Blimp):
    
    
        self.Blimp = Blimp
        
        all_points = self.Blimp.all_points
        
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
            pv_power = self.Blimp.eng.mw2pv(mW_power)

            # string for each group is nested in list for each percent
            group_string = self.Blimp.build_strings (X = galvo_x[group], Y = galvo_y[group], \
                                                    duration = self.Blimp.duration, laser_power = pv_power, \
                                                    is_spiral = 'true', spiral_revolutions = self.Blimp.spiral_revolutions, \
                                                    spiral_size = self.Blimp.spiral_size, num_spirals = self.Blimp.num_spirals)   
                                                                 
            group_list.append(group_string)
                
        #merge each group into a single string
        self.all_groups_mp = self.Blimp.groups_strings(self.Blimp.inter_group_interval, group_list, SLM_trigger = True)
        
        
        #init numpy arrays from tiffs
        mask_path = os.path.join(self.Blimp.output_folder, 'PhaseMasks')
        tiff_list = [os.path.join(mask_path,file) for file in os.listdir(mask_path) if file.endswith('.tiff') or file.endswith('.tif')]
        self.mask_list = [tifffile.imread(tiff) for tiff in tiff_list]
 
        print('{} Phase mask tiffs found'.format(len(tiff_list)))
        
        
    def run_experiment(self):  
        

        #arrays of precaculated frame locations in memory
        self.repeat_arrays = self.Blimp.precalculate_and_load_first(self.mask_list)
        
        ##thread so pycontrol does not stall
        slm_thread = Thread(target=self.Blimp.load_precalculated_triggered, args = [self.repeat_arrays])
        slm_thread.start()
        
        self.mp_output = self.Blimp.pl.SendScriptCommands(self.all_groups_mp)
        
        
        


            
