import numpy as np
import os
import win32com.client

class prairie_interface():
    def __init__(self):
        '''class to drive PrairieView based on behavioural events '''
        # Start PrairieLink
        self.pl = win32com.client.Dispatch('PrairieLink.Application')

        # Connect to PrairieLInk client
        try:
            self.pl.Connect()
            print('PV connection successful')
        except:
            raise Exception("Failed to connect to PV")
            
            
    def load_markpoints(self, f_path):
        '''loads a gpl or xml into markpoints, takes argument of full path to file, clears existing points'''
        self.pl.SendScriptCommands('-LoadMarkPoints ' + f_path + ' ' + 'True')
    
    def run_markpoints(self):
        self.pl.SendScriptCommands('-MarkPoints')
