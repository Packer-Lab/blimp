import matlab.engine
import yaml
import os
import time
import random
import numpy as np
import tifffile
from threading import Thread
from utils.utils_funcs import load_mat_file
from distutils.dir_util import copy_tree

class EasyTest():

    def __init__(self, Blimp):

        '''
        experiment to stimulate as large set of cells on half of go trials and a small set of cells on nogo trials 

        '''
        self._blimp = Blimp

        self.save_path = os.path.join(self._blimp.output_folder)

        self.subset_perms = self._blimp.yaml_dict['subset_perms']

        # list of subset size from largest to smallest, used for pre-calculation
        self.subset_sizes = self._blimp.yaml_dict['subset_sizes']
        # list to randomly choose subset size from
        self.subset_choose = self._blimp.yaml_dict['subset_sizes']      

            
        # the path to each percent save file, will percentage (p) and subset iteration (s) in file name
        # order of nested lists is important here
        self.subset_paths = [os.path.join(self.save_path, str(p) + '_' + str(s)) for s in range(self.subset_perms) for p in self.subset_sizes]

         # makes iterating easier
        self.subset_sizes = self.subset_sizes * self.subset_perms
        
        self.subsets_markpoints_strings, self.subsets_tiffs = self._init_subsets()

        self.all_groups_mp, self.repeat_arrays = self._init_easy()


    def _init_subsets(self):

        print('Building percent files')

        markpoints_strings = []
        tiffs = []
        for subset, path in zip(self.subset_sizes, self.subset_paths):
            #try 10 times to chose a subset that can position galvos
            for attempt in range(50):

                try:
                    _point_obj = self._blimp.eng.Main(self._blimp.naparm_path, 'processAll', 0, 'GroupSize', 
                                                      float(subset), 'splitPoints', 1, 'subsetSize', float(subset), 
                                                      'Save', 1, 'SavePath', path)
                    break
                except Exception as e:
                    if attempt == 49:
                        print('could not build points obejct after 50 attempts')
                        print(e)
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
            print('mw power is {}'.format(mW_power))
            print('pv power  is {}'.format(pv_power))
            if pv_power > 1000 or mW_power > 500:
                print('PV power is > 1000!!')
                time.sleep(5)
                raise ValueError

            # string for each group is nested in list for each percent
            group_string = self._blimp.build_strings(X = galvo_x, Y = galvo_y, duration = self._blimp.duration, 
                                                    laser_power = pv_power, is_spiral = 'true',
                                                    spiral_revolutions = self._blimp.spiral_revolutions, 
                                                    spiral_size = self._blimp.spiral_size, num_spirals = self._blimp.num_spirals)

            markpoints_strings.append(group_string)

            mask_path = os.path.join(path ,'PhaseMasks')

            tiff = [os.path.join(mask_path,file) for file in os.listdir(mask_path) if file.endswith('.tiff') or file.endswith('.tif')]
            assert len(tiff) == 1, 'Subset experiment currently only works with single groups'
            tiffs.append(tiff)


        assert len(markpoints_strings) == len(self.subset_sizes) == len(tiffs)

        print('Subset files built successfully')

        return markpoints_strings, tiffs

    def _init_easy(self):

        _points_path = next(os.path.join(self._blimp.naparm_path,file) for file in os.listdir(self._blimp.naparm_path) 
                                             if file.endswith('_Points.mat'))

        self.all_points = load_mat_file(_points_path)['points']
        #copy the phase masks
        copy_tree(os.path.join(self._blimp.naparm_path, 'PhaseMasks'), os.path.join(self._blimp.output_folder, 'PhaseMasks'))
        #copy the whole naparm directory in case of future issues
        copy_tree(self._blimp.naparm_path, os.path.join(self._blimp.output_folder, 'naparm'))

        # into foxy ratio format
        galvo_x = np.asarray(self.all_points['centroid_x']).squeeze() / 512
        galvo_y = np.asarray(self.all_points['centroid_y']).squeeze() / 512

        assert len(galvo_x) == len(galvo_y)

        mW_power = self._blimp.group_size * self._blimp.mWperCell
        print('group size is {}'.format(self._blimp.group_size))
        print('mw power is {}'.format(mW_power))

        pv_power = self._blimp.mw2pv(mW_power)
        print('PV power is {}'.format(pv_power))

        num_groups = len(galvo_x)
        group_list = []

        for group in range(num_groups):
            # string for each group is nested in list for each percent
            group_string = self._blimp.build_strings (X = galvo_x[group], Y = galvo_y[group], \
                                                    duration = self._blimp.duration, laser_power = pv_power, \
                                                    is_spiral = 'true', spiral_revolutions = self._blimp.spiral_revolutions, \
                                                    spiral_size = self._blimp.spiral_size, num_spirals = self._blimp.num_spirals)
            group_list.append(group_string)

        #merge each group into a single string
        all_groups_mp = self._blimp.groups_strings(self._blimp.inter_group_interval, group_list, SLM_trigger = True,
                                                        n_repeats=self._blimp.num_repeats)

        #init numpy arrays from tiffs
        mask_path = os.path.join(self._blimp.output_folder, 'PhaseMasks')
        tiff_list = [os.path.join(mask_path,file) for file in os.listdir(mask_path) if file.endswith('.tiff') or file.endswith('.tif')]
        mask_list = [tifffile.imread(tiff) for tiff in tiff_list]

        print('{} Phase mask tiffs found'.format(len(tiff_list)))

        #arrays of precaculated frame locations in memory
        repeat_arrays = self._blimp.sdk.precalculate_masks(mask_list, num_repeats=self._blimp.num_repeats)

        print('Easy group built')
        return all_groups_mp, repeat_arrays


    def slm_trial(self):
        ''' called when an SLM trial is initiated '''
        if 'easy' in self._blimp.slm_print:
            self.easy_trial()
        elif ' test' in self._blimp.slm_print:
            self.test_trial()
        else:
            raise ValueError

    def easy_trial(self):
        print('easy trial')
        # the threaded function
        slm_thread = Thread(target=self._blimp.sdk.load_precalculated_triggered, args = [self.repeat_arrays])
        slm_thread.start()
        time.sleep(0.01)
        # this function laods the 15ms trigger sequences to the hardware and begins the sequence
        self.mp_output = self._blimp.prairie.pl.SendScriptCommands(self.all_groups_mp)
        self._blimp.write_output(self._blimp.trial_runtime, self._blimp.trial_number, self._blimp.barcode, 'all_cells_stimulated')




    def test_trial(self):

        # randomly choose a percent to run  
        print('test trial')
        trial_subset = random.choice(self.subset_choose)
        rand_idx = random.choice(np.where(np.array(self.subset_sizes)==trial_subset)[0])
        subset_run = self.subset_sizes[rand_idx]
        trial_path = self.subset_paths[rand_idx]
        trial_string = self.subsets_markpoints_strings[rand_idx]
        mask = self.subsets_tiffs[rand_idx]

        print('Stimming {} cells'.format(subset_run))

        save_str = 'Subset cells experiment, Go trial, stimulating {} cells. File path is {}'.format(subset_run, trial_path)
        self._blimp.write_output(self._blimp.trial_runtime, self._blimp.trial_number, self._blimp.barcode, save_str)

        self._blimp.sdk.load_mask(mask)

        # this function laods the 15ms trigger sequences to the hardware and begins the sequence
        self.mp_output = self._blimp.prairie.pl.SendScriptCommands(trial_string)
        
        

    def nogo_trial(self):
        ''' called when an SLM trial is initiated '''
        #randomly choose a percent to run
        trial_subset = random.choice(self.subset_choose)
        rand_idx = random.choice(np.where(np.array(self.subset_sizes)==trial_subset)[0])
        subset_run = self.subset_sizes[rand_idx]
        trial_path = self.subset_paths[rand_idx]
        trial_string = self.subsets_markpoints_strings[rand_idx]
        mask = self.subsets_tiffs[rand_idx]

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
        

        
     









