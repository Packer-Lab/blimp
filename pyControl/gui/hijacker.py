import numpy as np

class hijack():
    '''class to hijack into the pycontrol framework and run full python commands based on lines printed in the task'''
    def __init__(self):
        #run the next printed line as python code?
        self.run_next = False
        #the line to run as python code
        self.code_line = None
        
        
    def set_state_machine(self, sm_info):
        print('hijacker initialised')
        self.sm_info = sm_info
        self.hijack_next = sm_info['variables']['hijack_next']
        #this removes the extra quote marks around the string
        self.hijack_next = eval(self.hijack_next)
        
   
    def update(self, new_data, run_time):
        for i,nd in enumerate(new_data): 
            #the hijack signal and the code line are printed neighbouring in the same list
            if nd[0] == 'P' and nd[2] in self.hijack_next:
                self.code_line = new_data[i+1][2]
                break
     
        if self.code_line:
            x = eval(self.code_line)
            self.code_line = None
            print(x)

        
        
        
    
