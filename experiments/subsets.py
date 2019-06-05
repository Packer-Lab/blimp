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

        inherits an instance of the _blimp class

        '''
        self._blimp = Blimp

        self.save_path = os.path.join(self._blimp.output_folder)

        self.subset_perms = self._blimp.yaml_dict['subset_perms']

        #subset size, duplicated by number of permuations
        self.subset_sizes = self._blimp.yaml_dict['subset_sizes']

        # the path to each percent save file, will percentage (p) and subset iteration (s) in file name
        self.subset_paths = [os.path.join(self.save_path, str(p) + '_' + str(s))  for p in self.subset_sizes for s in range(self.subset_perms)]

        self.markpoints_strings, self.tiffs = self._init_trials()

        #makes iterating easier
        self.subset_sizes = self.subset_sizes * self.subset_perms



    def _init_trials(self):

        print('Building percent files')

        markpoints_strings = []
        tiffs = []
        for subset, path in zip(self.subset_sizes, self.subset_paths):
            #try 10 times to chose a subset that can position galvos
            for attempt in range(10):
                try:
                    _point_obj = self._blimp.eng.Main(self._blimp.naparm_path, 'processAll', 0, 'GroupSize', float(subset), 'splitPoints', 1, 'subsetSize', float(subset), 'Save', 1, 'SavePath', path)
                    break
                except:
                    if attempt == 9:
                        print('could not build points obejct after 10 attempt')
                        time.sleep(10)
                        raise ValueError
                    else:
                        print('matlab engine failed to build point object, trying again')
                        continue


            _split_obj = _point_obj['split_points']

            # into foxy ratio format
            galvo_x = np.asarray(_split_obj['centroid_x']).squeeze() / 512
            galvo_y = np.asarray(_split_obj['centroid_y']).squeeze() / 512

            #the shape of the point array shows the group size
            mW_power = subset * self._blimp.mWperCell
            pv_power = self._blimp.mw2pv(mW_power)

            if pv_power > 1000:
                print('PV power is > 1000!!')
                time.sleep(5)
                raise ValueError

            # string for each group is nested in list for each percent
            group_string = self._blimp.build_strings(X = galvo_x, Y = galvo_y, duration = self._blimp.duration, laser_power = pv_power, is_spiral = 'true',\
            spiral_revolutions = self._blimp.spiral_revolutions, spiral_size = self._blimp.spiral_size, num_spirals = self._blimp.num_spirals)

            markpoints_strings.append(group_string)

            mask_path = os.path.join(path ,'PhaseMasks')

            tiff = [os.path.join(mask_path,file) for file in os.listdir(mask_path) if file.endswith('.tiff') or file.endswith('.tif')]
            assert len(tiff) == 1, 'Subset experiment currently only works with single groups'
            tiffs.append(tiff)


        assert len(markpoints_strings) == len(self.subset_sizes) == len(tiffs)

        print('Subset files built successfully')

        return markpoints_strings, tiffs


    def slm_trial(self):
        ''' called when an SLM trial is initiated '''
        #randomly choose a percent to run
        rand_idx = random.randrange(len(self.subset_sizes))

        subset_run = self.subset_sizes[rand_idx]
        trial_path = self.subset_paths[rand_idx]
        trial_string = self.markpoints_strings[rand_idx]
        mask = self.tiffs[rand_idx]

        print('Stimming {} cells'.format(subset_run))

        save_str = 'Subset cells experiment, Go trial, stimulating {} cells. File path is {}'.format(subset_run, trial_path)
        self._blimp.write_output(self._blimp.trial_runtime, self._blimp.trial_number, self._blimp.barcode, save_str)

        self._blimp.sdk.load_mask(mask)

        # this function laods the 15ms trigger sequences to the hardware and begins the sequence
        self.mp_output = self._blimp.prairie.pl.SendScriptCommands(trial_string)


    def nogo_trial(self):
        ''' called when an SLM trial is initiated '''
        #randomly choose a percent to run
        rand_idx = random.randrange(len(self.subset_sizes))

        subset_run = self.subset_sizes[rand_idx]
        trial_path = self.subset_paths[rand_idx]
        trial_string = self.markpoints_strings[rand_idx]
        mask = self.tiffs[rand_idx]

        #change the uncaging power in the string to 0
        _space_split = trial_string.split(' ')
        power_idx= [idx+1 for idx, el in enumerate(_space_split) if el == 'Uncaging']

        for idx in power_idx:
            _space_split[idx] = '0'
        
        trial_string = (' ').join(_space_split)

        print('Nogo {} cells'.format(subset_run))

        save_str = 'Subset cells experiment, Nogo Trial, {} cells. File path is {}'.format(subset_run, trial_path)
        self._blimp.write_output(self._blimp.trial_runtime, self._blimp.trial_number, self._blimp.barcode, save_str)

        ##the threaded function
        self._blimp.sdk.load_mask(mask)

        # this function laods the 15ms trigger sequences to the hardware and begins the sequence
        self.mp_output = self._blimp.prairie.pl.SendScriptCommands(trial_string)









