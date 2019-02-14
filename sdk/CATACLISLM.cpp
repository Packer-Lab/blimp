/*
BOSS SDK test (BOSSSLMOD... CATACLISLM...)
Date: 2016-08-10
Description: What it will do - parse folder, load images, compute sequence, wait for triggers, loop
Authors: Lloyd Russell, Henry Dalgleish, Adam Packer
*/

#include "stdafx.h"                          // Only #include's targetver.h.
#include <vector>
#include <cstdio>
#include <conio.h>                           // for kbhit() declaration.
#include <iostream>
#include <cstring>
#include <string>
#include <math.h> 
#include <fstream>
#include <chrono>                            // measure time
#include "Overdrive_SDK.h"
#pragma comment(lib, "Overdrive_SDK")
#include "dirent.h"
using namespace std;
using namespace std::chrono;

bool is_p_mask(string fname) {
	bool p_mask;
	if (fname.compare((fname.find_last_of(".") + 1), 3, "bmp") == 0)
	{
		p_mask = true;
	}
	else
	{
		p_mask = false;
	}
	return p_mask;
}

static void Consume_keystrokes()
// -------------------- Consume_keystrokes ------------------------------------
// Utility function to use up the keystrokes used to interrupt the display
// loop.
// ----------------------------------------------------------------------------
{
	// Get and throw away the character(s) entered on the console.
	int k = 0;
	while ((!k) || (k == 0xE0))  // Handles arrow and function keys.
	{
		k = _getch();
	}
	return;
}

static bool Precalculate_then_triggered_write(
	int num_masks,
	int num_loops,
	unsigned char **bmpArray,
	const int board_number,
	Overdrive_SDK& sdk,
	const float trigger_timeout_s)
	// -------------------- Precalculate_then_triggered_write ---------------------
	// This function demonstrates pre-calculating N hologram patterns then writing
	// the N frame sequences to the SLM, controlled by an external trigger.
	// ----------------------------------------------------------------------------
{
	puts("\nPress any key to exit AFTER some triggers received..\n");
	// Get the SLM into an assumed starting phase, before precalculating the
	// frame sequences. Here, we start with all pixels at half wave phase.
	std::vector<unsigned char> initial_phase(512U * 512U, 0x7F);
	// Fill very first phase mask with rand vals range 0-255 so don't overshoot first phase mask
	for (int r = 0; r < 512; r++)
	{
		for (int c = 0; c < 512; c++)
		{
			initial_phase[r, c] = rand() % 256;
		}
	}
	unsigned int n_bytes = 0;
	bool okay = sdk.Precompute_frames(initial_phase.data(), &n_bytes);
	std::vector<unsigned char> dummy(n_bytes);
	if (okay)
	{
		okay = sdk.Retrieve_precomputed_frames(dummy.data());
	}

	// Set the SLM to use an external trigger to start a frame sequence write.
	// At the stage, the hardware should not be sending triggers to the SLM.
	if (okay)
	{
		okay = sdk.Use_trigger_for_new_hologram(true, trigger_timeout_s);
	}

	// Fill the SDK's two queues with the initial phase frames.
	// Actually, filling one queue makes it think first trigger is two and you get the mask you want!
	// so comment out next line AP20160814
	//sdk.Write_precomputed_frames(board_number, dummy.data());
	sdk.Write_precomputed_frames(board_number, dummy.data());

	// Precalculate a set of hologram patterns. 
	std::vector<unsigned char> *frame_sequence = NULL;
	frame_sequence = new std::vector<unsigned char>[num_masks];

	int i = 0;
	while ((okay) && (i < num_masks))
	{
		unsigned int frame_buffer_byte_count = 0;
		okay = sdk.Precompute_frames(bmpArray[i],
			&frame_buffer_byte_count);
		if (okay)
		{
			frame_sequence[i].resize(frame_buffer_byte_count);
			okay = sdk.Retrieve_precomputed_frames(frame_sequence[i].data());
		}
		++i;
	}

	// Fill up queues with the first phase mask??
	//sdk.Write_precomputed_frames(board_number, frame_sequence[0].data());
	//sdk.Write_precomputed_frames(board_number, frame_sequence[0].data());

	// Now we've completed the pre-calculation, write to the SLM.
	i = 0;
	int j = 0;
	int count = 0;
	while ((okay) && (j < num_loops) && (!_kbhit()))
	{
		while ((okay) && (i < num_masks) && (!_kbhit()))
		{
			okay = sdk.Write_precomputed_frames(board_number,
				frame_sequence[i].data());
			if ((i == 0) && (j == 0))
			{
				cout << "First trigger received, so first phase mask displaying now.\n";
			}
			else
			{
				cout << "SLM thinks triggers received: " << count + 1 << " Relevant trigger count: " << count << " Loop: " << j + 1 << " Pattern: " << i << "\n";
			}

			++i;
			++count;
		}
		++j;
		i = 0;
	}

	count = count - 1; // incremented count at the 'end' of the loop.. but we're not done!

	// display the last phase mask
	if (count < (num_loops*num_masks))
	{
		okay = sdk.Write_precomputed_frames(board_number, frame_sequence[num_masks - 1].data());
		cout << "SLM thinks triggers received: " << count + 2 << " Relevant trigger count: " << count + 1 << " Loop: " << j << " Pattern: " << num_masks << "\n";
		count++;
	}

	cout << "\nSend a trigger to write a blank phase mask and exit,\nOR hit Ctrl-C to exit, leaving last phase mask on SLM.\n";
	okay = sdk.Write_overdrive_image(board_number, initial_phase.data());

	if ((okay) && count < num_loops*num_masks)    // Loop finished early but not because of error, must be keystroke
	{
		// Rewrite the initial all-gray phase.
		okay = sdk.Write_overdrive_image(board_number, initial_phase.data());
		okay = sdk.Use_trigger_for_new_hologram(false, trigger_timeout_s);
		cout << "okay = 1. detected keystroke. wrote flat field. turned triggering off.\n";
		Consume_keystrokes();
	}

	// Turn off triggered writes, whether we've had a previous error, or not.
	if (okay)
	{
		okay = sdk.Use_trigger_for_new_hologram(false, trigger_timeout_s);
		cout << "okay = 1. use trigger successfully set to false.\n";
	}
	else
	{
		// We had an error, but try to turn off triggering. Leave the existing
		// error status flag unchanged.
		sdk.Use_trigger_for_new_hologram(false, trigger_timeout_s);
		cout << "okay !=1. set trigger to false.\n";
	}

	return okay;
}


// -------------------- main --------------------------------------------------
// Simple example using the Overdrive_SDK DLL to send a sequence of phase
// targets to a single 512x512 SLM.
// This code yields a console application that will loop until the user presses
// a key. 
// This application uses the first (or only) 512 SLM that it detects on the
// PCIe bus.
// ----------------------------------------------------------------------------
int main(const int argc, char* const argv[])
{
	puts("  _     ___      _    ___  __         ");
	puts(" /   /\\  |  /\\  /  |   |  (_  |  |\\/| ");
	puts(" \\_ /--\\ | /--\\ \\_ |_ _|_ __) |_ |  | ");
	puts("                                      ");
	puts("(Custom A? T? A? Command Line Interface for Spatial Light Modulator)");
	puts("");

	// HENRY'S SIMPLE DIR READER TO GET FILES IN A FOLDER
	vector<string> all_p_masks;
	DIR* p_root_dir = NULL;
	string str_input;
	cout << "Please enter directory: ";
	cin >> str_input;
	const char* dir_name = str_input.c_str();
	string dir_str = dir_name;
	//cout << "Root dir = " << dir_name << endl;
	p_root_dir = opendir(dir_name);
	struct dirent* p_root = NULL;
	int num_masks = 0;
	while ((p_root = readdir(p_root_dir)))
	{
		string entry_name(p_root->d_name);
		if (is_p_mask(entry_name))
		{
			all_p_masks.push_back(dir_str + "/" + entry_name);
			cout << all_p_masks[num_masks] << endl;
			num_masks++;
		}
	}
	cout << "Number of phasemasks = " << num_masks << endl;
	closedir(p_root_dir);

	// Read phase masks from dir
	unsigned char **bmpArray = NULL;
	bmpArray = new unsigned char*[num_masks];
	unsigned char     *temp = NULL; // for flipping

	for (int i = 0; i < num_masks; i++)
	{
		// open file and read header
		FILE* f = fopen(all_p_masks[i].c_str(), "rb");
		unsigned char info[54];
		fread(info, sizeof(unsigned char), 54, f); // read the 54-byte header

		// extract image height and width from header
		int width = *(int*)&info[18];
		int height = *(int*)&info[22];
				
		// read additional headers eg color table
		// allocate and read data
		int size = 1 * width * height; // 1 is because there is 1 channel
		unsigned char* data = new unsigned char[size]; // allocate 1 byte per pixel because 1 channel
		fread(data, sizeof(unsigned char), 1024, f); // there is some header here, looks like palette/color table
		fread(data, sizeof(unsigned char), size, f); // read the rest of the data at once
		fclose(f);

		// Check BMP values are correct
		// for (int r = 0; r < 512; r++)
		//{
		//	for (int c = 0; c < 512; c++)
		//	{
		//		printf("%u ", (int)data[(r * 512) + c]);
		//	}
		//}

		// drop bmp data into bmpArray
		int numbytes = width * height * sizeof(unsigned char);
		bmpArray[i] = new unsigned char[numbytes];
		bmpArray[i] = data; 

		// flip order of the rows... vertical... ?
		temp = new unsigned char[numbytes];
		int r1 = 0;
		for (int r2 = 511; r2 > -1; r2--)
		{
			for (int c = 0; c < 512; c++)
			{
				//temp = bmpArray[i];
				temp[(r1 * 512) + c] = bmpArray[i][(r2 * 512) + c];
			}
			r1++;
		}
		bmpArray[i] = temp;

	}
	
	// Ask for user input on number of desired loops
	printf("Enter number of loops: ");
	int num_loops;
	cin >> num_loops;

	// Construct an Overdrive_SDK instance with Overdrive capability.
	const unsigned int bits_per_pixel = 8U;
	const unsigned int pixel_dimension = 512U;
	const bool         is_nematic_type = true;
	const bool         RAM_write_enable = true;
	const char* const  regional_lut_file = "slm3331_at1064_P8_OD.txt";
	unsigned int       max_display_frames = 10;
	bool               use_GPU_if_available = true;
	const int          board_number = 1;
	const float        trigger_timeout_s = 180.0f;

	unsigned int n_boards_found = 0U;
	bool okay = true;

	Overdrive_SDK sdk(bits_per_pixel, pixel_dimension, &n_boards_found,
		&okay, is_nematic_type, RAM_write_enable,
		use_GPU_if_available, regional_lut_file,
		max_display_frames);

	// Initialize some key SLM parameters. When using Overdrive, be sure to load
	// a linear LUT to the SLM (this is a separate step from providing the
	// Overdrive regional LUT, above).
	if (okay)     // SDK started up okay?
	{
		// puts(sdk.Get_version_info());
		enum { e_n_true_frames = 6 };
		okay = sdk.Set_true_frames(e_n_true_frames) &&
			sdk.SLM_power(true) &&
			sdk.Load_linear_LUT(board_number);
		if (okay)
		{
			// puts((sdk.Interrupts_enabled(board_number)) ?
			// "Interrupts enabled." : "Interrupts disabled.");
		}
	}
        
        
    // not sure what this is during translation (JR)
	if (okay) // make sure output pulse is on even though this is default behaviour
	{
		sdk.Use_external_pulse_on_flip(true);
	}

	// Now run one of the loops, toggling between the two ramp images.
	if (okay)
	{
		okay = Precalculate_then_triggered_write(num_masks, num_loops, bmpArray,
			board_number, sdk, trigger_timeout_s);
	}

	// Error reporting, if anything went wrong.
	if (!okay)
	{
		puts(sdk.Get_last_error_message());
	}

	return (okay) ? EXIT_SUCCESS : EXIT_FAILURE;
}