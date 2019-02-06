from lxml import objectify
from lxml import etree


class ParseMarkpoints():  
    
    ''' parses gpls or xmls from markpoints into python variables'''

    def __init__(self, xml_path=None, gpl_path=None):
        
        #super(ParseMarkpoints, self).__init__()
        
        self.xml_path = xml_path
        self.gpl_path = gpl_path
        
        if self.gpl_path:            
            self.parse_gpl()
            
        if self.xml_path:
            self.parse_xml()

       
        
    def parse_gpl(self):
        
        '''extract information from naparm gpl file'''
        
        gpl = etree.parse(self.gpl_path)

        self.Xs = []
        self.Ys = []
        self.is_spirals = []
        self.spiral_sizes = []

        for elem in gpl.iter():

            if elem.tag == 'PVGalvoPoint':
                self.Xs.append(elem.attrib['X'])
                self.Ys.append(elem.attrib['Y'])
                self.is_spirals.append(elem.attrib['IsSpiral'])
                #the spiral size gpl attrib contains a positive and negative number for 
                #some reason. This takes just the positive, may cause errors later
                self.spiral_sizes.append(elem.attrib['SpiralSize'].split(' ')[0])
                
            
    def parse_xml(self):

        '''extract requried information from xml into python lists'''

        xml = etree.parse(self.xml_path)

        self.laser_powers = []
        self.spiral_revolutions = []
        self.durations = []
        self.initial_delays = []
        self.repetitions = []
        
        for elem in xml.iter():

            if elem.tag == 'PVMarkPointElement':
                self.laser_powers.append(elem.attrib['UncagingLaserPower'])
                self.repetitions.append(elem.attrib['Repetitions'])
                
            elif elem.tag == 'PVGalvoPointElement':
                self.durations.append(elem.attrib['Duration'])
                self.spiral_revolutions.append(elem.attrib['SpiralRevolutions'])
                self.initial_delays.append(elem.attrib['InitialDelay'])
                
               
        #detect if a dummy point has been sent and remove it if so
        if self.laser_powers[0] == '0':
            self.dummy = True
            self.laser_powers.pop(0)
            self.spiral_revolutions.pop(0)
            self.durations.pop(0)
            self.initial_delays.pop(0)
            self.repetitions.pop(0)
            
        
    def build_strings(self, **kwargs):
    
        '''builds string using variables from parsed gpls and xmls that can be sent via prairie link'''

        for k,v in kwargs.items():
            setattr(self,k,v)
            
        markpoints_strings = []
        
        
        #check this against PV documentaion, probably shouldn't have the 'spiral_revolution' argument here
        settings_string = '{0} {1} {2} {3} {4} {5} {6} {7} 0.12 '.format(self.X,self.Y,self.duration,'Uncaging',self.laser_power,self.is_spiral,self.spiral_size,self.spiral_revolutions)
    
        #repeat num spirals times
        markpoints_string = settings_string * int(self.num_spirals)
        
        #snip the inter-spiral-delay off the last point and add the markpoints command
        markpoints_string  = '-mp ' + markpoints_string[:-6]
                   
        return markpoints_string
        
        
    def groups_strings(self,inter_group_interval, group_list):
    
        '''
        takes an input of n_groups length markpoints_string list and concatenates to one markpoints command string
        groups are stimmed with an interval os inter_group_interval (ms)     
                  
        '''
        
        n_groups = len(group_list)
        
        assert n_groups > 1, 'must give at least 2 markpoints strings to concantenate'
     
        all_groups = ''
        
        for ind, group in enumerate(group_list):
                     
            #pop off the -mp from all groups following group 1
            if ind != 0:
                group = group[4:]
            
            all_groups += group
            
            if ind != n_groups-1:
                all_groups += ' ' + str(inter_group_interval) + ' '
                
            
        return all_groups
        
        
    
    
    def build_dummy(self, **kwargs):
        
        for k,v in kwargs.items():
            setattr(self,k,v)
        
    
        return '-MarkPoints {0} {1} {2} {3} {4} {5} {6} {7}'.format(self.Xs[0], self.Ys[0], '1', 'Uncaging', '0', 'True', '1', '1')
            
            
        
        
        

    
    
    
    
    
    
    
    
    
    
    
    
    
    
     
    
                    
    
    
    
    
    
    
    
    
    
    
    
    
    


