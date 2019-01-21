from lxml import objectify
from lxml import etree


class ParseMarkpoints():  
    
    ''' parses gpls or xmls from markpoints into python variables'''

    def __init__(self, xml_path=None, gpl_path=None):
        
        super(ParseMarkpoints, self).__init__()
        
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
        self.delays = []
        self.repetitions = []
        
        for elem in xml.iter():

            if elem.tag == 'PVMarkPointElement':
                self.laser_powers.append(elem.attrib['UncagingLaserPower'])
                self.repetitions.append(elem.attrib['Repetitions'])
                
            elif elem.tag == 'PVGalvoPointElement':
                self.durations.append(elem.attrib['Duration'])
                self.spiral_revolutions.append(elem.attrib['SpiralRevolutions'])
                self.delays.append(elem.attrib['InitialDelay'])
                
               
        #detect if a dummy point has been sent and remove it if so
        if self.laser_powers[0] == '0':
            self.dummy = True
            self.laser_powers.pop(0)
            self.spiral_revolutions.pop(0)
            self.durations.pop(0)
            self.delays.pop(0)
            self.repetitions.pop(0)
            
        
    def build_strings(self):
    
        '''builds string using variables from parsed gpls and xmls that can be sent via prairie link'''
        
        markpoints_strings = []
        
        for X,Y,duration,laser_power,is_spiral,spiral_size,spiral_revolutions\
        in zip(self.Xs,self.Ys,self.durations,self.laser_powers,self.is_spirals,self.spiral_sizes,self.spiral_revolutions):
        
            markpoints_string = '-MarkPoints {0} {1} {2} {3} {4} {5} {6} {7}'.format(X,Y,duration,'Uncaging',laser_power,is_spiral,spiral_size,spiral_revolutions)
            
            markpoints_strings.append(markpoints_string)
            
        return markpoints_strings
        
    
    def build_dummy(self):
    
        return '-MarkPoints {0} {1} {2} {3} {4} {5} {6} {7}'.format(self.Xs[0], self.Ys[0], '1', 'Uncaging', '0', 'True', '1', '1')
            
            
        
        
        

    
    
    
    
    
    
    
    
    
    
    
    
    
    
     
    
                    
    
    
    
    
    
    
    
    
    
    
    
    
    


