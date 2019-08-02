import warnings
warnings.filterwarnings("ignore")
import time
import os
import sys
sys.path.append("..")

from utils.parse_markpoints import ParseMarkpoints
from utils.prairie_interface import PrairieInterface
from utils.utils_funcs import threshold_detect, load_mat_file
from sdk.slm_sdk import SLMsdk
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

from lxml import objectify
from lxml import etree
import numpy as np
import copy

class AutoNaparm2(ParseMarkpoints, PrairieInterface):

    def __init__(self, naparm_path, naparm_rate=1000):
    
        self.naparm_path = naparm_path
        self.naparm_rate = naparm_rate
        
        self.get_paths()  
        
        ParseMarkpoints.__init__(self, xml_path=self.xml_path, gpl_path=self.gpl_path)  
        PrairieInterface.__init__(self)
        
        self.mask_list = self.convert_tiffs(self.tiff_list)
        self.num_groups = len(self.mask_list)
        self.stim_timings()
        try:
            self.sdk = SLMsdk()
            self.sdk.SLM_connect()
            
            mask_pointers = self.sdk.precalculate_masks(self.mask_list, num_repeats=self.n_repeats)
            
            slm_thread = Thread(target=self.sdk.load_precalculated_triggered, args = [mask_pointers])
            slm_thread.start()
        except:
            print(colored('I COULD NOT CONNECT TO THE SLM CLOSE BLINK / OTHER AUTONAPARMS I WILL TRY AGAIN IN 3 SECONDS','yellow','on_red', attrs=['reverse', 'blink']))
            time.sleep(3)
            raise
            


        self.new_xml()
        
        
    def get_paths(self):           
        for file in os.listdir(self.naparm_path):
            if file.endswith('.xml') and 'AutoNaparm' not in file:
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
            try:
                for file in os.listdir(os.path.join(self.naparm_path, 'PhaseMasks')):
                    if file.endswith('.tif') or file.endswith('.tiff'):
                        self.tiff_list.append(os.path.join(self.naparm_path, 'PhaseMasks', file))
            except:
                print(colored('WOHHH ARE YOU SURE THATS A NAPARM FOLDER!? PRESS CTR-C AND START AGAIN','yellow','on_red', attrs=['reverse', 'blink']))
                time.sleep(1000)
                    
                    
    def convert_tiffs(self, tiff_list):
        return [tifffile.imread(tiff) for tiff in tiff_list]
        
        
    def stim_timings(self):
        
        slm_arr = np.fromfile(self.to_slm, dtype=float)

        self.total_time = len(slm_arr) / self.naparm_rate
        
        slm_times = threshold_detect(slm_arr, 1)
        
        self.n_repeats = len(slm_times) / self.num_groups
        
        assert self.n_repeats.is_integer()
        self.n_repeats = int(self.n_repeats)
        
        slm_diff = np.diff(slm_times)
        print(len(slm_arr))
        
        # time difference between groups on each trial
        self.inter_group_intervals = slm_diff[0:self.num_groups-1]
        #the time difference between groups of stimulations
        self.inter_trial_interval = slm_diff[self.num_groups-1]

        
    def new_xml(self):
        
        tree = etree.parse(self.xml_path)
        root = tree.getroot()

        markpoint_elems = root.findall('PVMarkPointElement')
        
        for i,point in enumerate(markpoint_elems):
            
            # mutate xml elems so no external trigger required    
            point.attrib['TriggerFrequency'] = 'Never'
            
            galvo_elem_point = next(node for node in point.getiterator() if node.tag == 'PVGalvoPointElement')
            
            #information about each group from ParseMarkpoints does not include dummy
            group_idx = i-1
            
            # durations and repetitions are from the ParseMarkpoints class
            stim_length = (int(self.durations[group_idx]) + 0.12) * int(self.repetitions[group_idx])
            # this is a diff so has len durations - 1
            inter_group_interval = self.inter_group_intervals[group_idx-1]
            
            #time in ms to move galvos to trigger position (not actually moved) and deliver the trigger
            trigger_len = 1.12
            
            if i == 0:
                assert point.attrib['UncagingLaserPower'] == '0', 'Need to use naparm with dummy'
                #delay by the time between the end of one trial and the start of the next - the delay of the trigger
                galvo_elem_point.attrib['InitialDelay']  = str(self.inter_trial_interval - inter_group_interval - trigger_len)
                continue


            galvo_elem_point.attrib['InitialDelay'] = '0'
            
            if i == len(markpoint_elems) - 1:
                continue
            
            #add the trigger lasers
            slm_trigger = copy.deepcopy(point)

            slm_trigger.attrib['UncagingLaser'] = 'Trigger'
            slm_trigger.attrib['UncagingLaserPower'] = '5' #volts (1000 PV)
            slm_trigger.attrib['AsyncSyncFrequency'] = 'None'
            slm_trigger.attrib['Repetitions'] = '1'

            galvo_elem_slm = next(node for node in slm_trigger.getiterator() if node.tag == 'PVGalvoPointElement')
            

            galvo_elem_slm.attrib['InitialDelay'] = str(inter_group_interval - stim_length - trigger_len) 
            
            galvo_elem_slm.attrib['Duration'] = '1'
            galvo_elem_slm.attrib['SpiralRevolutions'] = '1'
            
            parent = point.getparent()
            parent.insert(parent.index(point)+1, slm_trigger)
            
            #save the slm trigger with galvos at point 1 for appending to start after main loop
            if i == 1:
                slm_trigger_1 = copy.deepcopy(slm_trigger)
            
         
        root.insert(1, slm_trigger_1)
        
        self.autoxml_path = self.xml_path[:-4] + '_AutoNaparmXML.xml'        
        tree.write(self.autoxml_path)
        
        self.pl.SendScriptCommands('-LoadMarkPoints {}'.format(self.autoxml_path))
        self.pl.SendScriptCommands('-LoadMarkPoints {} True'.format(self.gpl_path))

        
    def fire(self):
        print('Beginning naparm sequence')
        self.pl.SendScriptCommands('-MarkPoints')
        
    def disconnect(self):
        self.sdk.SLM_disconnect()
        
        
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
    valid = {"yes": True, "y": True, "ye": True, "yeet": True, "hell yeah": True, "fuck yeah": True,
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
        
    #while True:
        
    print(colored('Paste Naparm path below to begin','white','on_red', attrs=['reverse', 'blink']))

    
    path_found = False
    
    while not path_found:
        naparm_path = input()
        naparm_path = naparm_path.replace('"', '')
        naparm_path = os.path.normpath(naparm_path)
        if not os.path.exists(naparm_path):
            print('file directory not found please enter again')
        else:
            print(colored('File path found', 'yellow'))
            path_found = True
            
    #initialise auto naparm
    try:
        an = AutoNaparm2(naparm_path= naparm_path)
    except:
        print('got an error')
        an = AutoNaparm2(naparm_path= naparm_path)

    #t_series = query_yes_no('Do you want to image during this Naparm? SORRY THIS IS CURRENTLY NOT IMPLEMENTED DO IT MANUALLY')
    #take me out at some point
    t_series = False
    print(colored('This Naparm will take {} seconds, if you want to image please update PV t-series settings'.format(an.total_time), 'yellow'))
    print(colored('DONT FORGET TO RECORD A PAQ!!!', 'red'))
    
    if t_series:
        print(colored('OK, initialising matlab engine for read raw data stream', 'yellow'))
        
        eng = matlab.engine.start_matlab()
  

    print(colored('*************Your laser power is {} PV********************'.format(an.laser_powers[0]), 'red'))
    ready = query_yes_no('ARE YOU READY TO FIRE?!!!!!')
    
    if ready: 
    
        # if t_series:
            # print(colored('Initialising Read Raw Data Stream', 'yellow'))
            # eng.PrairieLink_RawDataStream(nargout=0)
        
        an.fire()
            
    else:
        print(colored('OK try again', 'red'))
        time.sleep(2)
 
                    
                    
                    
                    
        
        
        
        



