import os
from ctypes import *
import time
import sys
import numpy as np
import imageio
import tifffile
class SLMsdk():

    def __init__(self, LUT = 'slm_h2_encrypt_noPhaseWrap.txt', blank_image = "512white.bmp"):
          
        # Load the DLL
        # Blink_SDK_C.dll, Blink_SDK.dll, FreeImage.dll and wdapi1021.dll
        # should all be located in the same directory as the program referencing the library
        
        #need to chdir into the sdk directory (Where this script is located) in order to load dlls
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)
        print("hello")
        
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
        
        okay = self.Is_slm_transient_constructed_func(self.sdk, c_bool(1))
        assert okay
        
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

        self.Calculate_transient_frames_func = self.slm_lib.Calculate_transient_frames
        self.Calculate_transient_frames_func.argtypes = (c_longlong, POINTER(c_ubyte), POINTER(c_uint))
        self.Calculate_transient_frames_func.restype = c_bool
        
        self.Retrieve_transient_frames_func = self.slm_lib.Retrieve_transient_frames
        self.Retrieve_transient_frames_func.argtypes = (c_longlong, POINTER(c_ubyte))
        self.Retrieve_transient_frames_func.restype = c_bool
        
        self.Write_transient_frames_func = self.slm_lib.Write_transient_frames
        self.Write_transient_frames_func.argtypes = (c_longlong, c_int, POINTER(c_ubyte), c_bool, c_bool, c_uint)
        self.Write_transient_frames_func.restype = c_bool

        self.Delete_SDK_func = self.slm_lib.Delete_SDK
        #for some reason giving this function an extra argument makes it work
        self.Delete_SDK_func.argtypes = (c_longlong, c_bool)

        self.error_func = self.slm_lib.Get_last_error_message
        #for some reason giving this function an extra argument makes it work
        self.error_func.argtypes = (c_longlong, c_bool)
        # function will now return user readable error message
        self.error_func.restype = c_char_p
        
        self.Is_slm_transient_constructed_func = self.slm_lib.Is_slm_transient_constructed
        #for some reason giving this function an extra argument makes it work
        self.Is_slm_transient_constructed_func.argtypes = (c_longlong, c_bool)
        self.Is_slm_transient_constructed_func.restype = c_bool
        

      
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
        max_transients = c_uint(5)
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
        
    
    def load_mask(self, mask, wait_for_trigger = False):
    
        '''loads the phase mask specified in 'mask' to the SLM'''
        
        mask = tifffile.imread(mask)
        
        if wait_for_trigger:
            self.Write_overdrive_image_func(self.sdk, 1, mask.ctypes.data_as(POINTER(c_ubyte)), 1, 0)
        else:
            self.Write_overdrive_image_func(self.sdk, 1, mask.ctypes.data_as(POINTER(c_ubyte)), 0, 0)

    
    def precalculate_masks(self, mask_list, num_repeats = 1):
        
        '''takes input mask_list, a list of numpy arrays containing phase masks
           outputs pointers to memory location of precaculated masks
        '''
        
        #list of pointers to locations of phase mask arrays in memory 
        mask_pointers = [mask.ctypes.data_as(POINTER(c_ubyte)) for mask in mask_list]
               
    
        #counts how many bytes required to store mask. Initial value set here is ignored and overwritten by Calculate_transient_frames_func
        byte_count = c_uint(0)

        precalc_arrays = []
                        
        # set to false if errors in mask writing 
        okay = True
        
        for i,pt in enumerate(mask_pointers):
    
            if okay:
            
                # precalculate frames and save them to memory
                #the the SLM into the previous phase and calculate transient frames
                if i == 0:
                    okay = self.Write_overdrive_image_func(self.sdk, 1, mask_pointers[-1], 0, 0)
                else:
                    okay = self.Write_overdrive_image_func(self.sdk, 1, mask_pointers[i-1], 0, 0)
                    
                okay = self.Calculate_transient_frames_func(self.sdk, pt, byte_count)
           
            if okay:
                # empty character array to store precalculated frame
                precalc_array = (c_ubyte * byte_count.value)()   
                
                # retrieve the precaulated frames as an unsigned character array
                okay = self.Retrieve_transient_frames_func(self.sdk, precalc_array)                            
                precalc_arrays.append(precalc_array)
            
            assert okay, 'Error writing precalculated frames to memory'

        #repeat the precalculated list
        repeat_arrays = precalc_arrays * num_repeats    
        
        return repeat_arrays

      
    def load_precalculated_triggered(self, repeat_arrays):
        
        okay = True
        print('Ready to trigger')
        
        # Write_transient_frames_func = self.slm_lib.Write_transient_frames
        # Write_transient_frames_func.argtypes = (c_longlong, c_int, POINTER(c_ubyte), c_bool, c_bool, c_uint)
        # Write_transient_frames_func.restype = c_bool
        
        for arr in repeat_arrays:
          
            okay = self.Write_transient_frames_func(self.sdk, c_int(1), arr, c_bool(1), c_bool(1), c_uint(0))

        assert okay, 'Failed to write frames to board'      
        print('completed trigger sequence')
                
        
    def SLM_disconnect(self):
        
        ''' power down and disconnect kernel from SLM '''
        
        # Turn the SLM power off
        self.SLM_power_func(self.sdk, c_bool(0))
        
        # Always call Delete_SDK before exiting
        self.Delete_SDK_func(self.sdk, c_bool(1))

        print('Disconnected from SLM and powered down')



    
    
