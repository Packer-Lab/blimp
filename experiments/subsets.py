import matlab.engine
import yaml
import os
import time
import random
import numpy as np
from threading import Thread

class Subsets():

    def __init__(self, Blimp):

        '''
        experiment to run a random subset of cells, defined in the subset_sizes list
        currently only works with a single group of size subset_sizes[idx]

        inherits an instance of the Blimp class

        '''
        self.Blimp = Blimp

        self.save_path = os.path.join(Blimp.output_folder)

        self.subset_perms = self.Blimp.yaml_dict['subset_perms']

        #subset size, duplicated by number of permuations 
        self.subset_sizes = self.Blimp.yaml_dict['subset_sizes']

        # the path to each percent save file, will percentage (p) and subset iteration (s) in file name
        self.subset_paths = [os.path.join(self.save_path, str(p) + '_' + str(s))  for p in self.subset_sizes for s in range(self.subset_perms)]

        self.markpoints_strings, self.tiffs = self.init_trials()

        #makes iterating easier
        self.subset_sizes = self.subset_sizes * self.subset_perms



    def init_trials(self):

        print('Building percent files')

        markpoints_strings = []
        tiffs = []
        for subset, path in zip(self.subset_sizes, self.subset_paths):

            point_obj = self.Blimp.eng.Main(self.Blimp.naparm_path, 'processAll', 0, 'GroupSize', float(subset), 'splitPoints', 1, 'subsetSize', float(subset), 'Save', 1, 'SavePath', path)

            split_obj = point_obj['split_points']
 
            # into foxy ratio format
            galvo_x = np.asarray(split_obj['centroid_x']).squeeze() / 512
            galvo_y = np.asarray(split_obj['centroid_y']).squeeze() / 512

            #the shape of the point array shows the group size
            mW_power = subset * self.Blimp.mWperCell
            pv_power = self.Blimp.mw2pv(mW_power)

            # string for each group is nested in list for each percent
            group_string = self.Blimp.build_strings(X = galvo_x, Y = galvo_y, duration = self.Blimp.duration, laser_power = pv_power, is_spiral = 'true',\
            spiral_revolutions = self.Blimp.spiral_revolutions, spiral_size = self.Blimp.spiral_size, num_spirals = self.Blimp.num_spirals)

            markpoints_strings.append(group_string)

            mask_path = os.path.join(path ,'PhaseMasks')

            tiff = [os.path.join(mask_path,file) for file in os.listdir(mask_path) if file.endswith('.tiff') or file.endswith('.tif')]
            assert len(tiff) == 1, 'Subset experiment currently only works with single groups'
            tiffs.append(tiff)


        assert len(markpoints_strings) == len(self.subset_sizes) == len(tiffs)

        print('Percent files built successfully')

        return markpoints_strings, tiffs 


    def run_experiment(self):

        ''' called when an SLM trial is initiated '''

        #randomly choose a percent to run
        rand_idx = random.randrange(len(self.subset_sizes))

        subset_run = self.subset_sizes[rand_idx]
        trial_path = self.subset_paths[rand_idx]
        trial_string = self.markpoints_strings[rand_idx]
        mask = self.tiffs[rand_idx]

        print('Stimming {} cells'.format(subset_run))

        save_str = 'Subset cells experiment, stimulating {} cells. File path is {}'.format(subset_run, trial_path)
        self.Blimp.write_output(self.Blimp.trial_runtime, self.Blimp.trial_number, self.Blimp.barcode, save_str)

        ##the threaded function
        slm_thread = Thread(target=self.Blimp.sdk.load_mask, args = [mask])
        slm_thread.start()

        time.sleep(0.01)
        
        # this function laods the 15ms trigger sequences to the hardware and begins the sequence 
        self.mp_output = self.Blimp.prairie.pl.SendScriptCommands(trial_string)
        













