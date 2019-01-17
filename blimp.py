import numpy as np
from sdk.SLM_sdk import SLM_sdk

class blimp():

    '''detailed description goes here'''
    
    def __init__(self):
        
        # this will work on windows
        self.sdk = SLM_sdk() 
        self.sdk.SLM_connect()
        
        #initialise variables take the same name as events in pycontrol call functions in this class
        self.SLM_trial = 'SLM_trial'
        # the event ID indicating the SLM_trial event has been published
        self.SLM_ID = None
        

          
    def set_state_machine(self, sm_info):
        
        '''initialise state machine variables from pycontrol'''
        
        events = sm_info['events']
        self.event_IDs = list(sm_info['events'].values())
        
        # get the ID of the SLM trial event
        if self.SLM_trial in events:
            self.SLM_ID = events[self.SLM_trial]
        
   
    def update(self, new_data, run_time):
        
        ''' called every time there is a new print, state or event in pycontrol'''
        
        #ID of any event that occurs
        new_ID = [nd[2] for nd in new_data if nd[0] == 'D' and nd[2] in self.event_IDs]
        
        # break function if no new event is found
        if not new_ID:
            return

        if new_ID[0] == self.SLM_ID:
            
            #call the SLM stimulation function
            self.fire_SLM()
            
            
    def fire_SLM(self):   
        self.sdk.load_mask(path)
           
           


        
        
        
