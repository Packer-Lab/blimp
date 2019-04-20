import numpy as np
import ruamel.yaml
from sdk.slm_sdk import SLMsdk
from utils.prairie_interface import PrairieInterface
from utils.parse_markpoints import ParseMarkpoints
import sys
import os
from datetime import datetime
import time
import matlab.engine
from pathlib import Path
import experiments


class Blimp(SLMsdk, PrairieInterface, ParseMarkpoints):
    def __init__(self):
        '''detailed description goes here'''
        
        # alows stopping and starting in the pycontrol gui
        if not hasattr(self, 'im_init'):
  
            #load yaml
            base_path = os.path.dirname(__file__)
            yaml_path = os.path.join(base_path, "blimp_settings.yaml")
        
            #the ruamel module preserves the comments and order of the yaml file
            yaml = ruamel.yaml.YAML() 
            with open(yaml_path, 'r') as stream:
                yaml_dict = yaml.load(stream)
                

            self.time_now = datetime.now().strftime('%Y-%m-%d-%H%M%S')
            
            self.naparm_path = yaml_dict['naparm_path']
            output_path = yaml_dict['output_path'] 
            
            self.output_folder = os.path.join(output_path, self.time_now)

            if not os.path.exists(self.output_folder):
                os.makedirs(self.output_folder)
                
            # save the current settings yaml into the todays folder
            with open(os.path.join(self.output_folder, '{}_blimp_settings.yaml'.format(self.time_now)), 'w+') as f:
                yaml.dump(yaml_dict, f)
                
            self.group_size = yaml_dict['group_size']
            
            self.duration = yaml_dict['duration']
            self.num_spirals = yaml_dict['num_spirals']
            self.spiral_revolutions = yaml_dict['spiral_revolutions']
            self.mWperCell = yaml_dict['mWperCell']
            self.inter_group_interval = yaml_dict['inter_group_interval']
            self.num_repeats = yaml_dict['num_repeats']
            
            #calculate spiral size as 0-1 ratio of fov size
            self.spiral_size = yaml_dict['spiral_size'] / (yaml_dict['FOVsize_UM_1x'] / yaml_dict['zoom'])
            
            # initialise the SLM sdk and prarie interface, inheriting attributes from these classses
            SLMsdk.__init__(self)
            PrairieInterface.__init__(self)
            ParseMarkpoints.__init__(self)
            # connect to the SLM
            try:
                self.SLM_connect() 
            except:
                print('close other SLM connections')
                time.sleep(5)
                raise
            
            #start the matlab engine
            print('Initialising matlab engine')
            self.eng = matlab.engine.start_matlab()
            print('matlab engine initialised')

            # get the points object for all target points
            points_obj = self.eng.Main(self.naparm_path, 'processAll', 1, 'GroupSize', self.group_size, 'SavePath', self.output_folder)
            self.all_points = points_obj['all_points']
            
            # the numbers of the SLM trials produced by pycontrol (error in task if not continous list of ints)
            self.SLM_tnums = []
            # the barcodes of the SLM trials 
            self.SLM_barcodes = []
            # the times of the SLM trials
            self.SLM_times = []
            
            self.run_time_prev = 0
            
            #get the experiment function defined in the yaml
            try:  
                self.experiment_class = getattr(experiments, yaml_dict['experiment'])
            except:
                raise Exception('Could not find experiment defined in yaml')
            

            # inits the experiment class with Blimp attributes (this is probably a horrible way of doing this)
            self.experiment = self.experiment_class(self)
            
            #set the uncaging laser power to 0 and open the uncaging shutter
            self.pl.SendScriptCommands('-SetLaserPower Uncaging 0')
            time.sleep(1)
            self.pl.SendScriptCommands('-OverrideHardShutter Uncaging open')
        
            # dont init the class more than once
            self.im_init = True

        
    def update(self, new_data, run_time):
        
        ''' called every time there is a new print, state or event in pycontrol '''
        
        #all prints that occur from the board
        pycontrol_print = [nd for nd in new_data if nd[0] == 'P']
        
        x = [nd for nd in new_data]
        
        if run_time < self.run_time_prev:
            self.__init__()
        self.run_time_prev = run_time        
        # break function if no new print statement is found
        if pycontrol_print:
            pycontrol_print = pycontrol_print[0][2]
        else:
            return
            
  

  

        # an SLM trial is initiated
        if 'Trigger SLM trial' in pycontrol_print:
            print('here')
        
      
            
            self.trial_runtime = round(run_time,4) # dont need more than ms precision
            # search the SLM trial string for the number and barcode
            space_split = pycontrol_print.split(' ')    
            self.trial_number = [space_split[i+1] for i,word in enumerate(space_split) if word == 'Number'][0]
            self.barcode = [space_split[i+1] for i,word in enumerate(space_split) if word == 'Barcode'][0]  
                   
            #append to the alignment lists                   
            self.SLM_tnums.append(self.trial_number)
            self.SLM_barcodes.append(self.barcode)           
            self.SLM_times.append(self.trial_runtime)
            
            #write to the output file
            #commented out as will probably leave this to the experiment file
            #self.write_output(self.trial_runtime, self.trial_number, self.barcode)
            
            # begin SLM trial    
            
            self.experiment.run_experiment() 


    def update_test(self):
        '''development function to test the update function called from pycontrol'''
        self.experiment.run_experiment() 

    def write_output(self, time_stamp=None, trial_number=None, barcode=None, info=None):
      
        #the txtfile to write alignent information to
        self.txtfile = os.path.join(self.output_folder, 'blimpAlignment.txt')
        with open(self.txtfile, 'a') as f:   
            f.write('Time stamp: {0}. Trial Number {1}. Barcode {2}. Info: {3} \n'.format(time_stamp, trial_number, barcode, info)) 


if __name__ == '__main__':
    Blimp()
        

