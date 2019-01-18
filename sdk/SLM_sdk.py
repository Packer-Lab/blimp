import os
from ctypes import *
from time import sleep
import sys
import imageio
import numpy as np

class SLM_sdk():

    def __init__(self, LUT = 'slm_h2_encrypt_noPhaseWrap.txt', blank_image = "512white.bmp"):
          
        # Load the DLL
        # Blink_SDK_C.dll, Blink_SDK.dll, FreeImage.dll and wdapi1021.dll
        # should all be located in the same directory as the program referencing the library
        
        #need to chdir into the sdk directory (Where this script is located) in order to load dlls
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)
        
        #load dlls
        cdll.LoadLibrary("Blink_SDK_C.dll")
        self.slm_lib = CDLL("Blink_SDK_C")
   
        #python 3 requries conversion to bytes for c_char_p, use plain string in python 2
        LUT = bytes(LUT, 'utf-8')
        self.lut_file = c_char_p(LUT)
        
        # Blank calibration image
        self.cal_image = imageio.imread(blank_image)
        
    def SLM_connect(self):
        
        # initialise required functions
        self.init_functions()
        # initialise hard coded settings
        self.SLM_settings()
        
        # A blank calibration image must be loaded to the SLM controller
        self.Write_cal_buffer_func(self.sdk, 1, self.cal_image.ctypes.data_as(POINTER(c_ubyte)))
        
        # A linear LUT must be loaded to the controller for OverDrive Plus
        self.Load_linear_LUT_func(self.sdk, 1)

        # Turn the SLM power on
        self.SLM_power_func(self.sdk, c_bool(1))
        

        
    def init_functions(self):
    
        ''' initiliases the C functions required to load images to the SLM '''
        
        self.create_SDK_func = self.slm_lib.Create_SDK
        self.create_SDK_func.argtypes = (c_uint, c_uint, POINTER(c_uint), POINTER(c_bool), c_bool, c_bool, c_bool, c_uint, c_char_p)
        # in python 3 the integer returned by create_SDK_func is bigger than 32 bit, so had to reassign the integer type to longlong
        self.create_SDK_func.restype = c_longlong

        self.Set_true_frames_func = self.slm_lib.Set_true_frames
        self.Set_true_frames_func.argtypes = (c_longlong, c_int)

        self.Write_cal_buffer_func = self.slm_lib.Write_cal_buffer
        self.Write_cal_buffer_func.argtypes = (c_longlong, c_int, POINTER(c_ubyte))

        self.Load_linear_LUT_func = self.slm_lib.Load_linear_LUT
        self.Load_linear_LUT_func.argtypes = (c_longlong, c_int)

        self.SLM_power_func =  self.slm_lib.SLM_power
        self.SLM_power_func.argtypes = (c_longlong, c_bool)

        self.Write_overdrive_image_func = self.slm_lib.Write_overdrive_image
        self.Write_overdrive_image_func.argtypes = (c_longlong, c_int, POINTER(c_ubyte), c_bool, c_bool)

        self.Delete_SDK_func = self.slm_lib.Delete_SDK
        #for some reason giving this function an extra argument makes it work
        self.Delete_SDK_func.argtypes = (c_longlong, c_bool)

        self.error_func = self.slm_lib.Get_last_error_message
        #for some reason giving this function an extra argument makes it work
        self.error_func.argtypes = (c_longlong, c_bool)
        # function will now return user readable error message
        self.error_func.restype = c_char_p
        
      
    def SLM_settings(self):
    
        '''input SLM settings here'''
        
        # Basic parameters for calling Create_SDK
        slm_resolution = c_uint(512)
        # currently only supports 8 bit depth
        bit_depth = c_uint(8)
        num_boards_found = c_uint(0)
        constructed_okay = c_bool(0)
        is_nematic_type = c_bool(1)
        RAM_write_enable = c_bool(1)
        use_GPU = c_bool(1)
        max_transients = c_uint(20)
        true_frames = c_int(3)
        
        # Call the Create_SDK constructor
        # Returns a handle that's passed to subsequent SDK calls
        self.sdk = self.create_SDK_func(bit_depth, slm_resolution, byref(num_boards_found), 
                                 byref(constructed_okay), is_nematic_type, 
                                 RAM_write_enable, use_GPU, max_transients, self.lut_file)

        if constructed_okay: 
            print('SLM connection established')
        else:
            SLM_error = self.error_func(self.sdk, c_bool(1)).decode('utf-8')
            raise Exception(SLM_error)
            
        # Load true frames setting onto the SLM
        self.Set_true_frames_func(self.sdk, true_frames)
        
    
    def load_mask(self, mask):
    
        '''loads the phase mask specified in 'mask' to the SLM'''
        
        mask = imageio.imread(mask)
        self.Write_overdrive_image_func(self.sdk, 1, mask.ctypes.data_as(POINTER(c_ubyte)), 0, 0)
        
    def SLM_disconnect(self):
        
        ''' power down and disconnect kernel from SLM '''
        
        # Always call Delete_SDK before exiting
        self.Delete_SDK_func(self.sdk, c_bool(1))
        
        # Turn the SLM power off
        self.SLM_power_func(self.sdk, c_bool(0))
        
        print('Disconnected from SLM and powered down')



    
    
