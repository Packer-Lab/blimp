import numpy as np
import ruamel.yaml
from sdk.slm_sdk import SLMsdk
from utils.prairie_interface import PrairieInterface
from utils.parse_markpoints import ParseMarkpoints
from utils.utils_funcs import load_mat_file, tangent
import sys
import os
from datetime import datetime
import time
from pathlib import Path
import experiments
import matlab.engine

class Blimp(SLMsdk, PrairieInterface, ParseMarkpoints):

    def __init__(self):
        '''
        interface between pycontrol, prarie view software and
        medowlark slm
        '''
        # alows stopping and starting in the pycontrol gui
        if not hasattr(self, '_im_init'):

            self.assign_from_yaml()

            self.time_now = datetime.now().strftime('%Y-%m-%d-%H%M%S')
            self.output_folder = os.path.join(self._output_path, self.time_now)

            if not os.path.exists(self.output_folder):
                os.makedirs(self.output_folder)

            # save the current settings yaml into the todays folder
            with open(os.path.join(self.output_folder, '{}_blimp_settings.yaml'.format(self.time_now)), 'w+') as f:
                _yaml.dump(self.yaml_dict, f)

            # connect to the SLM
            try:
                self.sdk.SLM_connect()
            except:
                print('close other SLM connections')
                time.sleep(5)
                raise

            # the numbers of the SLM trials produced by pycontrol (error in task if not continous list of ints)
            self.SLM_tnums = []
            # the barcodes of the SLM trials
            self.SLM_barcodes = []
            # the times of the SLM trials
            self.SLM_times = []
            self._run_time_prev = 0

            #get the experiment function defined in the yaml
            try:
                self.experiment_class = getattr(experiments, self.yaml_dict['experiment'])
            except:
                raise Exception('Could not find experiment defined in yaml')
            # inits the experiment class with and instance of the Blimp class (this is probably a horrible way of doing this)
            self.experiment = self.experiment_class(self)

            #set the uncaging laser power to 0 and open the uncaging shutter
            self.prairie.pl.SendScriptCommands('-SetLaserPower Uncaging 0')
            time.sleep(1)
            self.prairie.pl.SendScriptCommands('-OverrideHardShutter Uncaging open')

            # dont init the class more than once
            self._im_init = True

     @property
     def yaml_dict(self):
        #load yaml
        _base_path = os.path.dirname(__file__)
        _yaml_path = os.path.join(_base_path, "blimp_settings.yaml")

        #the ruamel module preserves the comments and order of the yaml file
        _yaml = ruamel.yaml.YAML()
        with open(_yaml_path, 'r') as stream:
            return _yaml.load(stream)

    @property
    def eng(self):
        print('starting matlab engine')
        eng = matlab.engine.start_matlab()
        print('matlab engine initialised')
        return eng

    @property
    def sdk(self):
        return(SLMsdk())

    @property
    def prairie(self):
        return(PrairieInterface())

    @property
    def mp_parser(self):
        return(ParseMarkpoints())

    def assign_from_yaml(self):
        self.group_size = self.yaml_dict['group_size']
        self.duration = self.yaml_dict['duration']
        self.num_spirals = self.yaml_dict['num_spirals']
        self.spiral_revolutions = self.yaml_dict['spiral_revolutions']
        self.mWperCell = self.yaml_dict['mWperCell']
        self.inter_group_interval = self.yaml_dict['inter_group_interval']
        self.num_repeats = self.yaml_dict['num_repeats']
        #calculate spiral size as 0-1 ratio of fov size
        self.spiral_size = self.yaml_dict['spiral_size'] / (self.yaml_dict['FOVsize_UM_1x'] / self.yaml_dict['zoom'])
        self.naparm_path = self.yaml_dict['naparm_path']
        self._output_path = self.yaml_dict['output_path']

    def mw2pv(self, x):
        '''returns the PV value required for specific PV value based on DigitalPowerMeasurments notebook fitting'''
        _popt_path = self.yaml_dict['popt_path']
        _popt = np.load(_popt_path)

        return(tangent(x, *_popt))

    def update(self, new_data, _run_time):

        ''' called every time there is a new print, state or event in pycontrol '''

        #all prints that occur from the board
        _pycontrol_print = [nd for nd in new_data if nd[0] == 'P']

        if _run_time < self._run_time_prev:
            self.__init__()

        self._run_time_prev = _run_time
        # break function if no new print statement is found
        if _pycontrol_print:
            _pycontrol_print = _pycontrol_print[0][2]
        else:
            return

        # an SLM trial is initiated
        if 'Trigger SLM trial' in _pycontrol_print:

            self.trial_runtime = round(_run_time,4) # dont need more than ms precision
            # search the SLM trial string for the number and barcode
            __space_split = _pycontrol_print.split(' ')
            self.trial_number = [_space_split[i+1] for i,word in enumerate(_space_split) if word == 'Number'][0]
            self.barcode = [_space_split[i+1] for i,word in enumerate(_space_split) if word == 'Barcode'][0]

            #append to the alignment lists
            self.SLM_tnums.append(self.trial_number)
            self.SLM_barcodes.append(self.barcode)
            self.SLM_times.append(self.trial_runtime)

            # begin SLM trial
            self.experiment.run_experiment()

    def update_test(self):
        '''development function to test the update function called from pycontrol'''
        self.trial_runtime = 1
        self.trial_number = 1
        self.barcode = 1
        self.experiment.run_experiment()

    def write_output(self, time_stamp=None, trial_number=None, barcode=None, info=None):

        #the txtfile to write alignent information to
        self.txtfile = os.path.join(self.output_folder, 'blimpAlignment.txt')
        with open(self.txtfile, 'a') as f:
            f.write('Time stamp: {0}. Trial Number {1}. Barcode {2}. Info: {3} \n'.format(time_stamp, trial_number, barcode, info))

if __name__ == '__main__':
    Blimp()
