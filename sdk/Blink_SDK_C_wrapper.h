//
//:  Blink_SDK_C_wrapper for programming languages that can interface with DLLs
//
//   (c) Copyright Boulder Nonlinear Systems 2014 - 2014, All Rights Reserved.
//   (c) Copyright Meadowlark Optics 2015, All Rights Reserved.

#ifndef BLINK_SDK_CWRAPPER_H_
#define BLINK_SDK_CWRAPPER_H_

#ifdef SDK_WRAPPER_EXPORTS
#define BLINK_WRAPPER_API __declspec(dllexport)
#else
#define BLINK_WRAPPER_API
#endif

#ifdef __cplusplus
extern "C" { /* using a C++ compiler */
#endif

  typedef struct Blink_SDK Blink_SDK; /* make the class opaque to the wrapper */

  BLINK_WRAPPER_API Blink_SDK* Create_SDK(unsigned int SLM_bit_depth,
                                          unsigned int SLM_resolution,
                                          unsigned int* n_boards_found,
                                          bool *constructed_ok,
                                          bool is_nematic_type = true,
                                          bool RAM_write_enable = true,
                                          bool use_GPU_if_available = true,
                                          size_t max_transient_frames = 20U,
                                          const char* static_regional_lut_file = 0);

  BLINK_WRAPPER_API void Delete_SDK(Blink_SDK *sdk);

  BLINK_WRAPPER_API
  bool Is_slm_transient_constructed(Blink_SDK *sdk);

  BLINK_WRAPPER_API
  bool Write_overdrive_image(Blink_SDK *sdk, int board,
                             const unsigned char* target_phase,
                             bool wait_for_trigger,
                             bool external_pulse);

  BLINK_WRAPPER_API
  bool Calculate_transient_frames(Blink_SDK *sdk, const unsigned char* target_phase,
                                  unsigned int* byte_count);

  BLINK_WRAPPER_API
  bool Retrieve_transient_frames(Blink_SDK *sdk, unsigned char* frame_buffer);

  BLINK_WRAPPER_API
  bool Write_transient_frames(Blink_SDK *sdk, int board,
                              const unsigned char* frame_buffer,
                              bool wait_for_trigger,
                              bool external_pulse);

  BLINK_WRAPPER_API
  bool Read_transient_buffer_size(Blink_SDK *sdk, const char*   filename,
                                  unsigned int* byte_count);

  BLINK_WRAPPER_API
  bool Read_transient_buffer(Blink_SDK *sdk,
                             const char*    filename,
                             unsigned int   byte_count,
                             unsigned char* frame_buffer);

  BLINK_WRAPPER_API
  bool Save_transient_frames(Blink_SDK *sdk,
                             const char*          filename,
                             const unsigned char* frame_buffer);

  BLINK_WRAPPER_API
  const char* Get_last_error_message(Blink_SDK *sdk);

  BLINK_WRAPPER_API
  bool Load_overdrive_LUT_file(Blink_SDK *sdk, const char* static_regional_lut_file);

  BLINK_WRAPPER_API
  bool Load_linear_LUT(Blink_SDK *sdk, int board);

  BLINK_WRAPPER_API
  const char* Get_version_info(Blink_SDK *sdk);

  BLINK_WRAPPER_API
  void SLM_power(Blink_SDK *sdk, bool power_state);

  // ----------------------------------------------------------------------------
  //  Write_image
  // ----------------------------------------------------------------------------
  BLINK_WRAPPER_API
  bool Write_image(Blink_SDK *sdk, 
                   int board, 
                   unsigned char* image, 
                   unsigned int image_size,
                   bool wait_for_trigger,
                   bool external_pulse);

  // ----------------------------------------------------------------------------
  //  Load_LUT_file
  // ----------------------------------------------------------------------------
  BLINK_WRAPPER_API bool Load_LUT_file(Blink_SDK *sdk, int board, char* LUT_file);

  // ----------------------------------------------------------------------------
  //  Compute_TF
  // ----------------------------------------------------------------------------
  BLINK_WRAPPER_API int Compute_TF(Blink_SDK *sdk, float frame_rate);

  // ----------------------------------------------------------------------------
  //  Set_true_frames
  // ----------------------------------------------------------------------------
  BLINK_WRAPPER_API void Set_true_frames(Blink_SDK *sdk, int true_frames);

  // ----------------------------------------------------------------------------
  //  Write_cal_buffer
  // ----------------------------------------------------------------------------
  BLINK_WRAPPER_API bool Write_cal_buffer(Blink_SDK *sdk, 
    int board, const unsigned char* buffer);



#ifdef __cplusplus
}
#endif


#endif // BLINK_SDK_CWRAPPER_H_