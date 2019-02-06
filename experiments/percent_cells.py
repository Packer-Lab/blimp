import matlab.engine
import yaml
import os
import time
import random
import numpy as np

class PercentCells():

    def __init__(self, Blimp):
    
        '''
        experiment to run a random subset of cells, defined in percentages list
        inherits blimp attributes (this may be angering the python gods)
        
        '''   
        self.Blimp = Blimp
                
        self.save_path = os.path.join(Blimp.output_folder)
        
        self.num_subsets = self.Blimp.yaml_dict['num_subsets']
        
        #percents, duplicated by number of subsets
        self.percents = self.Blimp.yaml_dict['percents']
        
        # the path to each percent save file, will percentage (p) and subset iteration (s) in file name
        self.percent_paths = [os.path.join(self.save_path, str(p) + '_' + str(s))  for p in self.percents for s in range(self.num_subsets)]
        
        #makes iterating easier
        self.percents = self.percents * self.num_subsets

        # build files required for stim, using JR PointsProcessor interface to LR SLMPhaseMaskMakerCUDA3D_v2
        print('Building percent files')
        
        self.markpoints_strings = self.get_markpoints_strings()
        
        
        print('Percent files built successfully')
        
        print(self.markpoints_strings[0])
        
        self.Blimp.pl.SendScriptCommands(self.markpoints_strings[0])
            
          
        
    def get_markpoints_strings(self): 
        
        markpoints_strings = []

        for percent, path in zip(self.percents, self.percent_paths):
        
            point_obj = self.Blimp.eng.PointsProcessor(self.Blimp.naparm_path, 'processAll', 0, 'GroupSize', 10, 'splitPoints', 1, 'splitPercent', float(percent), 'Save', 1, 'SavePath', path)
                  
            split_obj = point_obj['split_points']
            
            galvo_x = np.asarray(split_obj['Xv'])[0]
            galvo_y = np.asarray(split_obj['Yv'])[0]
        
            num_groups = len(galvo_x)
            
            # list of every groups string for a given percent iteration
            group_list = []
            
            for group in range(num_groups):
                
                #the shape of the point array shows the group size
                group_size = np.asarray(split_obj['points_array'][group]).shape[0]

                mW_power = group_size * self.Blimp.mWperCell                
                pv_power = self.Blimp.eng.mw2pv(mW_power)
                              
                # string for each group is nested in list for each percent
                group_string = self.Blimp.build_strings(X = galvo_x[group], Y = galvo_y[group], duration = self.Blimp.duration, laser_power = pv_power, is_spiral = 'true',\
                spiral_revolutions = self.Blimp.spiral_revolutions, spiral_size = self.Blimp.spiral_size, num_spirals = self.Blimp.num_spirals)
                
                group_list.append(group_string)
                
            #merge each group into a single string
            all_groups = self.Blimp.groups_strings(self.Blimp.inter_group_interval, group_list)
         
            # now build list of every percent iterations string with all groups
            markpoints_strings.append(all_groups)   

        assert len(markpoints_strings) == len(self.percents) == len(self.percent_paths)
        
        return markpoints_strings
        
        
    def run_experiment(self):
    
        ''' called when an SLM trial is initiated '''
    
        #randomly choose a percent to run       
        rand_ind = random.randrange(len(self.percents))
        
        percent_run = self.percents[rand_ind]
        trial_path = self.percent_paths[rand_ind]
        trial_string = self.markpoints_strings[rand_ind]
        
        print('Stimming {}% of cells'.format(percent_run))
        

        
        save_str = 'Percent cells experiment, stimulating {}% of cells. Naparm path is {}'.format(percent_run, trial_path)
        self.Blimp.write_output(self.Blimp.trial_runtime, self.Blimp.trial_number, self.Blimp.barcode, save_str)
        
        
        
        
        
        
        
        
        
        
        
        
        
