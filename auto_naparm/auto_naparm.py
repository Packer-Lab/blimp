import warnings
warnings.filterwarnings("ignore")
import time
import os
import sys
sys.path.append("..")
sys.path.append("/home/jamesrowland/Documents/Code/blimp/matlab")
from utils.parse_markpoints import ParseMarkpoints
#from utils.prairie_interface import PrairieInterface
#from utils import mat_loader as ml
#from sdk.slm_sdk import SLMsdk
import scipy.io
import yaml
import numpy as np
import imageio
import tifffile
import matplotlib.pyplot as plt
from threading import Thread
from pyfiglet import Figlet
import time
import matlab.engine

from asciimatics.effects import Stars, Print
from asciimatics.particles import RingFirework, SerpentFirework, StarFirework,  \
    PalmFirework, Explosion
from asciimatics.renderers import SpeechBubble, FigletText, Rainbow
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
from random import randint, choice

import colorama
from termcolor import colored, cprint
colorama.init()


#class auto_naparm(ParseMarkpoints, PrairieInterface):
class auto_naparm(ParseMarkpoints):
    
    def __init__(self, naparm_path, naparm_rate=1000):
        
        
        self.naparm_path = naparm_path
        self.naparm_rate = naparm_rate
        #self.get_yaml()
        self.get_paths()       
        #self.mask_list = self.convert_tiffs(self.tiff_list)
#        
        ParseMarkpoints.__init__(self, xml_path=self.xml_path, gpl_path=self.gpl_path)  
#            
#        self.galvo_positions()

        self.stim_timings()
        
#        self.markpoints_string()
#        
#        sdk = SLMsdk()
#        sdk.SLM_connect()
#        mask_pointers = sdk.precalculate_and_load_first(self.mask_list, num_repeats=self.n_repeats)
#        
#        slm_thread = Thread(target=sdk.load_precalculated_triggered, args = [mask_pointers])
#        slm_thread.start()
#        
#        PrairieInterface.__init__(self)


#    def get_yaml(self):
#        with open(r'C:\Users\User\Documents\Code\blimp\blimp_settings.yaml', 'r') as stream:
#                    self.yaml_dict = yaml.load(stream)
#               
    def get_paths(self):           
        for file in os.listdir(self.naparm_path):
            if file.endswith('.xml'):
                self.xml_path= os.path.join(self.naparm_path, file)
            elif file.endswith('gpl'):
                self.gpl_path = os.path.join(self.naparm_path, file)
            elif file.endswith('Points.mat'):
                self.points_path = os.path.join(self.naparm_path, file)
            elif file == 'ToPV_AllTrials.dat' or file == 'SpiralsAllTrials.dat':
                self.to_pv = os.path.join(self.naparm_path, file)
            elif file == 'ToSLM_AllTrials.dat' or file == 'SLMAllTrials.dat':
                self.to_slm = os.path.join(self.naparm_path, file)  
                        
            self.tiff_list = []
            for file in os.listdir(os.path.join(naparm_path, 'PhaseMasks')):
                if file.endswith('.tif') or file.endswith('.tiff'):
                    self.tiff_list.append(os.path.join(naparm_path, 'PhaseMasks', file))
#                    
#    def convert_tiffs(self, tiff_list):
#        return [tifffile.imread(tiff) for tiff in tiff_list]
#        
#    def galvo_positions(self):
#    
#        st = ml.load_mat_struct(self.points_path)
#        points = st['points']
#        
#        all_x_galvo = points.GroupCentroidX
#        all_y_galvo = points.GroupCentroidY
#        groupings = points.Group
#        self.num_groups = max(groupings)

#        self.galvo_x = []
#        self.galvo_y = []
#        
#        for group in range(1,self.num_groups+1):
#    
#            group_idx = np.where(groupings==group)
#            
#            # x and y galvo positions of all points in pixels
#            x_px = all_x_galvo[group_idx]
#            y_px = all_y_galvo[group_idx]
#            
#            # all elements should be the same (stolen from stack overflow)
#            assert list(x_px).count(x_px[0]) == len(x_px)
#            assert list(y_px).count(y_px[0]) == len(y_px)
#            
#            #into foxy ratio format
#            self.galvo_x.append(x_px[0] / 512)
#            self.galvo_y.append(y_px[0] / 512)
#            
#        print(self.laser_powers)

#        assert len(self.galvo_x) == len(self.galvo_y) == len(self.durations) == len(self.laser_powers)
#        
#    
    def stim_timings(self):
        
        pv_arr = np.fromfile(self.to_pv, dtype=float)
        slm_arr = np.fromfile(self.to_slm, dtype=float)
        
        self.total_time = len(slm_arr) / self.naparm_rate
        
#        #time between each SLM trigger
#        self.slm_diff = np.diff(np.where(np.diff(slm_arr) > 0))[0] / self.naparm_rate * 1000 #ms 

#        #the time between each PV trigger
#        self.pv_diff = np.diff(np.where(np.diff(pv_arr) > 0))[0] / self.naparm_rate * 1000  #ms
#        
#        #assumes that there is a trigger at t=0
#        num_stims = len(np.where(np.diff(pv_arr) > 0)[0]) + 1
#        self.n_repeats = num_stims / self.num_groups 
#        assert self.n_repeats.is_integer()
#        self.n_repeats = int(self.n_repeats)
                
#        
#    def markpoints_string(self):
#    
#        mp_strings = []

#        #currently only supporting evenly spaced groups
#        inter_group_interval = self.slm_diff[0]

#        spiral_size = self.yaml_dict['spiral_size'] / (self.yaml_dict['FOVsize_UM_1x'] / self.yaml_dict['zoom'])
#        spiral_revolutions = self.spiral_revolutions[0]

#        for group in range(self.num_groups):
#        
#            x = self.galvo_x[group]
#            y = self.galvo_y[group]
#            duration = self.durations[group]
#            laser_power = self.laser_powers[group]
#            #laser_power = pm.laser_powers[group]
#            num_spirals = self.repetitions[group]
#            
#            mp_string = self.build_strings(X=x,Y=y,duration=duration,laser_power=laser_power, \
#                                         is_spiral=True, spiral_size=spiral_size, \
#                                         spiral_revolutions=spiral_revolutions, num_spirals=num_spirals)

#            mp_strings.append(mp_string)
#            

#            
#            
#        self.all_groups_string = self.groups_strings(inter_group_interval=inter_group_interval, \
#                                              group_list=mp_strings, SLM_trigger=True, n_repeats=self.n_repeats)
#                                              
#    
#    def fire(self):
#        
#        self.pl.SendScriptCommands(self.all_groups_string)



def startup_animation(screen):
    scenes = []
    effects = []
    for _ in range(10):
        effects.append(
            Explosion(screen,
                      randint(3, screen.width - 4),
                      randint(1, screen.height - 2),
                      randint(20, 30),
                      start_frame=randint(0, 250)))

    effects.append(Print(screen,
                         FigletText("Welcome \nto \nNaparm", font='standard'),
                         screen.height // 2 - 10,
                         speed=1,
                         start_frame=100))

    scenes.append(Scene(effects, -1))

    screen.play(scenes, stop_on_resize=True, repeat=False)
    
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        print(colored(question + prompt, 'white', 'on_red', attrs=['reverse', 'blink']))
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
            
            
            
        
if __name__ == '__main__':
    
    clear = lambda: os.system('cls')
    clear()
    
    Screen.wrapper(startup_animation)
    
    print(colored('Paste Naparm path below to begin','white','on_red', attrs=['reverse', 'blink']))

    
    path_found = False
    
    while not path_found:
        naparm_path = os.path.normpath(input())
        if not os.path.exists(naparm_path):
            print('file directory not found')
        else:
            print(colored('File path found', 'yellow'))
            path_found = True
            
    #initialise auto naparm
    an = auto_naparm(naparm_path= naparm_path)
    
    t_series = query_yes_no('Do you want to image during this Naparm?')
    
    if t_series:
        print(colored('OK, initialising matlab engine for read raw data stream', 'yellow'))
        print(colored('This Naparm will take {} seconds, please update PV t-series settings'.format(an.total_time), 'white'))
        eng = matlab.engine.start_matlab()
  

    print(colored('*************Your laser power is {} PV********************', 'red'))
    ready = query_yes_no('ARE YOU READY TO FIRE?!!!!!'.format(5))#an.laser_powers[0]))
    
    if ready: 
    
        if t_series:
            print(colored('Initialising Read Raw Data Stream', 'yellow'))
            eng.PrairieLink_RawDataStream(nargout=0)
        
        an.fire()
    else:
        print(f2.renderText('GOODBYE'))

    
    
    
    
    
    
    
    
    
    
    
    
    
    

