from pyControl.utility import *
import hardware_definition as hw
from devices import *


states = ['trial_start', 'SLM_state', 'LED_state', 'detect_lick_nogo']
        
events = ['SLM_trial', 'LED_trial']

initial_state = 'trial_start'

##### set the parameters of the task here
## --------------------------------------------------------------------------------------

# autoreward parameters
v.consec_autoswitch = 3 #the number of consecutive earned rewards during autoreward phase to swtich to active phase 

# session parameters
v.reward_time = 60 # time that the solenoid is open during rewards (ms)
v.d_prime_threshold = 2


v.chanceSLM = 0.4 
v.chanceLED = 0.4
v.chanceNoGo = 0.2

    
v.lick_window = 2.5  # reward time window during which mouse has to lick (s)


# inter-trial-interval parameters
v.withold_len = [x / 10 for x in range(40, 61)] #time that the animal must withold licking, a list in 0.1 increments from 4-6, that can be sampled randomly
v.ITI = 5 # the inter-trial interval(S). This is also the time during which rewards are registered as recieved if the animal licks

# parameters for swtiching between autorewarded and not autorewarded conditions
v.miss_switch = 3 # the number of consecutive missed trials before the animal is switched back to autoreward

# the number of consecutive trials where the animal did not drink a reward before ending the framework
v.end_ignore = 10

v.pulse_len = 20 #length of the LED pulse (ms)
v.num_pulses = 5 #number of LED pulses

v.rolling_window_len = 10 #the length of the rolling d' window


##### initialise global task variables
# --------------------------------------------------------------------------------------

# general task counters
v.num_trials = 0 # count trials
v.num_rewards = 0 # the number of rewards delivered
v.num_ignored = 0
v.consecIgnored = 0 #the number of rewards that have been delieverd that the animal has not drunk
#v.rolling_counter = 0 #counts to 10 trials on a rolling basis

# counters for go and nogo trials
v.num_go = 0 # the total number of go trials
v.num_nogo = 0
v.consecGo = 0 # count the number of consecutive go and nogo trials
v.consecNoGo = 0

# the current trial state
v.isSLM = False
v.isLED = False
v.isNoGo = False


# trial outcome counters
v.rolling_hit = [] # rolling hit counter
v.num_misses = 0
v.num_rejections = 0
v.rolling_fa = [] #rolling fa counter

v.d_prime = 0

v.consecMiss = 0 #counts misses on not autorewarded trials

# reward counters
v.num_rewards_received = 0 # how many rewards the mouse has successfully recieved
v.reward_increment = True #whether to increment rewards. Stops multiple increments from mulitple licks
v.gave_reward = False #tell the ITI function whether a reward has just been delivered
v.drank_reward = False #whether the animal drank its reward

# autoreward task variables
v.num_autorewards = 0 #the number of times the animal has been autorewarded in one autoreward session
v.num_earned_rewards = 0 # how many times the mouse licks before autoreward arrives
v.consec_autocorrect  = 0 #how many consective earned rewards during autoreward

v.boost_autoreward = False # whether to give a boost autoreward after a few consecutive misses
v.num_boosts = 0 #the number of boost phases
v.num_boost_autorewards = 0

v.hit_rate = 'NaN'
v.false_alarm_rate = 'NaN'

v.pulses_done = 0 # the number of pulses of the LED

#misc variables
v.print_switch = True #print the switch between autoreward conditions only once
 


def trial_start(event):

    # randomly choose whether it's an LED, SLM or nogo trial
    if event == 'entry':

        v.num_trials += 1
        v.isSLM = withprob(v.chanceSLM)
        
        if v.isSLM:
            v.isNoGo = False
        else:
            v.isNoGo = True
            
        if v.isGo:
            timed_goto_state('SLM_state', 2*second)
        else:
            timed_goto_state('detect_lick_nogo', 2*second)
            
           

def SLM_state(event):    
    if event == 'entry':
        
        #call the blimp all optical stim function
        publish_event('SLM_trial')
        
        timed_goto_state('trial_start', 1*second)
        

        
def detect_lick_nogo(event):
    if event == 'entry':
        publish_event('SLM_trial')
        print('nogo trial')
        timed_goto_state('trial_start', 1*second)
            
        
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
