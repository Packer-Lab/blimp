import matlab.engine
import yaml
import os
import time
import random
import numpy as np

class Subsets():

    def __init__(self, Blimp):

        '''
        experiment to run a random subset of cells, defined in the subset_sizes list
        currently only works with a single group of size subset_sizes[idx]

        inherits blimp attributes (this may be angering the python gods)

        '''
        self.Blimp = Blimp

        self.save_path = os.path.join(Blimp.output_folder)

        self.subset_perms = self.Blimp.yaml_dict['subset_perms']

        #percents, duplicated by number of subsets
        self.subset_sizes = self.Blimp.yaml_dict['subset_sizes']

        # the path to each percent save file, will percentage (p) and subset iteration (s) in file name
        self.subset_paths = [os.path.join(self.save_path, str(p) + '_' + str(s))  for p in self.subset_sizes for s in range(self.subset_perms)]

        self.markpoints_strings, self.precalc_masks = init_trials(self)

        #makes iterating easier
        self.subset_sizes = self.subset_sizes * self.subset_perms



    def init_trials(self):

        print('Building percent files')

        markpoints_strings = []
        precalc_masks = []

        for subset, path in zip(self.subset_sizes, self.subset_paths):

            point_obj = self.Blimp.eng.PointsProcessor(self.Blimp.naparm_path, 'processAll', 0, 'GroupSize', , 'splitPoints', 1, 'splitPercent', float(percent), 'Save', 1, 'SavePath', path)

            split_obj = point_obj['split_points']

            galvo_x = np.asarray(split_obj['Xv'])[0]
            galvo_y = np.asarray(split_obj['Yv'])[0]

            #the shape of the point array shows the group size
            group_size = np.asarray(split_obj['points_array'][group]).shape[0]

            mW_power = group_size * self.Blimp.mWperCell
            pv_power = self.Blimp.eng.mw2pv(mW_power)

            # string for each group is nested in list for each percent
            group_string = self.Blimp.build_strings(X = galvo_x[0], Y = galvo_y[0], duration = self.Blimp.duration, laser_power = pv_power, is_spiral = 'true',\
            spiral_revolutions = self.Blimp.spiral_revolutions, spiral_size = self.Blimp.spiral_size, num_spirals = self.Blimp.num_spirals)

            #build string with SLM trigger
            trigger_string = self.Blimp.groups_strings(self.Blimp.inter_group_interval, [group_string], SLM_trigger=True)

            markpoints_strings.append(trigger_string)

            mask_path = os.path.join(self.Blimp.output_folder, 'PhaseMasks')

            tiff_list = [os.path.join(mask_path,file) for file in os.listdir(mask_path) if file.endswith('.tiff') or file.endswith('.tif')]
            assert len(tiff_list) == 1, 'Subset experiment currently only works with single groups'

            precalc_mask = self.Blimp.precalculate_masks(tiff_list)
            precalc_masks.append(precalc_mask)

        assert len(markpoints_strings) == len(self.subset_sizes) == len(self.percent_paths)

        print('Percent files built successfully')

        return markpoints_strings, precalculated_masks


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
