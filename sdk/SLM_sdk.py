# Example usage of Blink_SDK_C.dll
# Meadowlark Optics Spatial Light Modulators
# March 2 2015

import os
from ctypes import *
from scipy import misc
from time import sleep
import sys

class SLM_sdk():
    def __init__(self, LUT):
    
        ''' 
        class to build SDK to interface with medowlark SLM assumes running the same folder as the compiled blink c wrapper
        input: LUT, name / path to LUT file
               
        '''
        
        # Load the DLL
        # Blink_SDK_C.dll, Blink_SDK.dll, FreeImage.dll and wdapi1021.dll
        # should all be located in the same directory as the program referencing the
        # library
        cdll.LoadLibrary("Blink_SDK_C")
        slm_lib = CDLL("Blink_SDK_C")

        # Basic parameters for calling Create_SDK
        # may want to pass these as arguments in the future
        bit_depth = c_uint(8)
        slm_resolution = c_uint(512)
        num_boards_found = c_uint(0)
        constructed_okay = c_bool(0)
        is_nematic_type = c_bool(1)
        RAM_write_enable = c_bool(1)
        use_GPU = c_bool(0)
        max_transients = c_uint(10)


        LUT = bytes(LUT, 'utf-8')

        # OverDrive Plus parameters
        lut_file = c_char_p(LUT)

        # Basic SLM parameters
        true_frames = c_int(3)

        create_SDK_func = slm_lib.Create_SDK
        create_SDK_func.argtypes = (c_uint, c_uint, POINTER(c_uint), POINTER(c_bool), c_bool, c_bool, c_bool, c_uint, c_char_p)

        Set_true_frames_func = slm_lib.Set_true_frames
        Set_true_frames_func.argtypes = (c_int, c_int)

        Write_cal_buffer_func = slm_lib.Write_cal_buffer
        Write_cal_buffer_func.argtypes = (c_int, c_int, POINTER(c_ubyte))

        Load_linear_LUT_func = slm_lib.Load_linear_LUT
        Load_linear_LUT_func.argtypes = (c_int, c_int)

        SLM_power_func =  slm_lib.SLM_power
        SLM_power_func.argtypes = (c_int, c_bool)

        Write_overdrive_image_func = slm_lib.Write_overdrive_image
        Write_overdrive_image_func.argtypes = (c_int, c_int, POINTER(c_ubyte), c_bool, c_bool)

        Delete_SDK_func = slm_lib.Delete_SDK
        Delete_SDK_func.argtype = (c_int)

        # Call the Create_SDK constructor
        # Returns a handle that's passed to subsequent SDK calls
        self.sdk = create_SDK_func(bit_depth, slm_resolution, byref(num_boards_found), 
                                 byref(constructed_okay), is_nematic_type, 
                                 RAM_write_enable, use_GPU, max_transients, lut_file)


        if not constructed_okay:
            print("Blink SDK was not successfully constructed")
            # Always call Delete_SDK before exiting
            slm_lib.Delete_SDK(sdk)
            raise
    

# Blank calibration image
blank_image = r'C:\Users\User\Desktop\PhaseMasks_8bit_BOSS\PhaseMasks_8bit_BOSS\UCLsmall_LPphase16.tiff'
cal_image = misc.imread(blank_image, flatten = 0)

neuron_phase = r'C:\Users\User\Desktop\PhaseMasks_8bit_BOSS\PhaseMasks_8bit_BOSS\20150424_Neuron_LPphase.tiff'
tst_phase = r'C:\Users\User\Desktop\PhaseMasks_8bit_BOSS\PhaseMasks_8bit_BOSS\10spotsTight_LPphase.bmp'

# Arrays for image data
neuron = misc.imread(neuron_phase, flatten = 0)
tst = misc.imread(tst_phase, flatten = 0)

print("Blink SDK was successfully constructed")
print("Found %s SLM controller(s)" % num_boards_found.value)

# Set the basic SLM parameters
Set_true_frames_func(sdk, true_frames)
# A blank calibration image must be loaded to the SLM controller
Write_cal_buffer_func(sdk, 1, cal_image.ctypes.data_as(POINTER(c_ubyte)))
# A linear LUT must be loaded to the controller for OverDrive Plus
Load_linear_LUT_func(sdk, 1)

# Turn the SLM power on
SLM_power_func(sdk, c_bool(1))

Write_overdrive_image_func(sdk, 1, neuron.ctypes.data_as(POINTER(c_ubyte)), 0, 0)
sleep(2.5) # This is in seconds


# Always call Delete_SDK before exiting
Delete_SDK_func(sdk)




if __name__ == __main__:
    LUT = 'slm_h2_encrypt.txt'
    slm_sdk = SLM_sdk(LUT)
    


















