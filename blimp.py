import numpy as np
import yaml
from sdk.slm_sdk import SLMsdk
from utils.prairie_interface import PrairieInterface
import sys
import os
from datetime import datetime
import experiments


class Blimp(SLMsdk, PrairieInterface):

    '''detailed description goes here'''
    
    def __init__(self):
        
        #load yaml
        
        base_path = os.path.dirname(__file__)
        yaml_path = os.path.join(base_path, "blimp_settings.yaml")

        with open(yaml_path, 'r') as stream:
            yaml_dict = yaml.load(stream)
        
        self.naparm_path = yaml_dict['naparm_path']
        self.output_path = yaml_dict['output_path']
        
        #get the experiment function defined in the yaml
        try:  
            self.experiment_func = getattr(experiments, yaml_dict['experiment'])
        except:
            raise Exception('Could not find experiment defined in yaml')
        
        self.time_now = datetime.now().strftime('%Y-%m-%d-%H%M%S')
       
        
        # initialise the SLM sdk and prarie interface, inheriting attributes from these classses
        #SLMsdk.__init__(self)
        PrairieInterface.__init__(self)
        
        # connect to the SLM
        #self.SLM_connect() 
        
        # the numbers of the SLM trials produced by pycontrol (error in task if not continous list of ints)
        self.SLM_tnums = []
        #the barcodes of the SLM trials 
        self.SLM_barcodes = []
        #the times of the SLM trials
        self.SLM_times = []
        
        self.run_time_prev = 0
   
    def update(self, new_data, run_time):
        
        ''' called every time there is a new print, state or event in pycontrol '''
        
        #ID of any event that occurs
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
        if 'SLM trial' in pycontrol_print:
        
            # search the SLM trial string for the number and barcode
            space_split = pycontrol_print.split(' ')    
            trial_number = [space_split[i+1] for i,word in enumerate(space_split) if word == 'Number'][0]
            barcode = [space_split[i+1] for i,word in enumerate(space_split) if word == 'Barcode'][0]  
                   
            #append to the alignment lists                   
            self.SLM_tnums.append(trial_number)
            self.SLM_barcodes.append(barcode)           
            self.SLM_times.append(run_time)
            
            #write to the output file
            self.write_output(run_time, trial_number, barcode)
            
            # begin SLM trial    
            self.experiment_func()           
    
    
    def write_output(self, time_stamp=None, trial_number=None, barcode=None):
      
        #the txtfile to write alignent information to
        self.txtfile = os.path.join(self.output_path, '{}_blimpAlignment.txt'.format(self.time_now))
        with open(self.txtfile, 'a') as f:   
            f.write('Time stamp: {0}. Trial Number {1}. Barcode {2}. \n'.format(time_stamp, trial_number, barcode)) 


if __name__ == '__main__':
    Blimp()
        

