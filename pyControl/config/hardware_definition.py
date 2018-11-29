# This hardware definition specifies that 3 pokes are plugged into ports 1-3 and a speaker into
# port 4 of breakout board version 1.2.  The houselight is plugged into the center pokes solenoid socket.

from devices import *
import pyb
from pyControl.hardware import *

board = Breakout_1_2()

# Instantiate digital output connected to BNC_1.
LED = Analog_LED(port=board.port_4)
Lickometer = Lickometer(port=board.port_1)
solenoid = Lickometer.SOL_2
