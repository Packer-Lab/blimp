from lxml import objectify
from lxml import etree


class parse_markpoints():  
    
    ''' parses gpls or xmls from markpoints into python variables'''

    def __init__(self, xml_path=None, gpl_path=None):
        
        super(parse_markpoints, self).__init__()
        
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
                self.spiral_sizes.append(elem.attrib['SpiralSize'])
                
            
    def parse_xml(self):

        '''extract requried information from xml into python lists'''

        xml = etree.parse(self.xml_path)

        self.laser_powers = []
        self.spiral_revolutions = []
        self.durations = []
        self.delays = []

        for elem in xml.iter():

            if elem.tag == 'PVMarkPointElement':
                self.laser_powers.append(elem.attrib['UncagingLaserPower'])

            elif elem.tag == 'PVGalvoPointElement':
                self.durations.append(elem.attrib['Duration'])
                self.spiral_revolutions.append(elem.attrib['SpiralRevolutions'])
                self.delays.append(elem.attrib['InitialDelay'])
                
                
    def build_strings(self):
    
        '''builds string using variables from parsed gpls and xmls that can be sent via prairie link'''
        
        markpoints_strings = []
        
        for X,Y,duration,laser_power,is_spiral,spiral_size,spiral_revolutions\
        in zip(self.Xs,self.Ys,self.durations,self.laser_powers,self.is_spirals,self.spiral_sizes,self.spiral_revolutions):
        
            markpoints_string = '-MarkPoints {0} {1} {2} {3} {4} {5} {6} {7}'.format(str(X),str(Y),str(duration),'Uncaging',str(laser_power),is_spiral,str(spiral_size),str(spiral_revolutions))
            
            markpoints_strings.append(markpoints_string)
            
        return markpoints_strings
            
            
        
        
        

    
    
    
    
    
    
    
    
    
    
    
    
    
    
     
    
                    
    
    
    
    
    
    
    
    
    
    
    
    
    


