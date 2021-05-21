# Code made to generate BCI Compatible Syntectic Data
# Data Format Standards Obtained from http://docs.openbci.com/Hardware/03-Cyton_Data_Format

import os
#import serial
import time
from time import sleep
from random import gauss
from math import sqrt, pi, sin
import struct
from pylsl import StreamInfo, StreamOutlet

freq = 250  # Hz
EOT = b'$$$'  # End Of Transmission characters
BCIsettings = b'060110'  # Default Channel Settings
header = b'\xA0'  # OpenBCI header
footer = b'\xC0'  # OpenBCI footer
numChannels = 40
uV = [0] * numChannels

# LSL Setup
info = StreamInfo('AURA_power', 'EEG', numChannels, freq, 'float32', 'myuid01')
# append some meta-data
channels = info.desc().append_child("channels")
# for c in ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]:
for i in range(numChannels):
    c = f'C{i+1}'
    channels.append_child("channel") \
        .append_child_value("label", c) \
        .append_child_value("unit", "microvolts") \
        .append_child_value("type", "EEG")
 # next make an outlet
outlet = StreamOutlet(info)


# Synthectic Algorithm adapted from OpenBCI Processing Code
def synthesizeData(freq):
    sine_freq_Hz = 10
    sine_phase_rad = [0] * numChannels
    uVbytes = []
    for chan in range(numChannels):
        val_uV = gauss(0, 1) * sqrt(freq/2)
        if chan == 0:
            val_uV *= 10  # scale one channel higher

        elif chan == 1:  # add sine wave at 10 Hz at 10 uVrms
            sine_phase_rad[chan] += 2*pi*sine_freq_Hz/freq
            if(sine_phase_rad[chan] > 2*pi):
                sine_phase_rad[chan] -= 2*pi
            val_uV += 10 * sqrt(2)*sin(sine_phase_rad[chan])

        elif chan == 2:  # 50 Hz interference at 50 uVrms
            sine_phase_rad[chan] += 2*pi * 50 / freq  # 60Hz
            if (sine_phase_rad[chan] > 2*pi):
                sine_phase_rad[chan] -= 2*pi
            val_uV += 50 * sqrt(2)*sin(sine_phase_rad[chan])  # 20 uVrms

        elif chan == 3:  # 60 Hz interference at 50 uVrms
            sine_phase_rad[chan] += 2*pi * 60 / freq  # 50 Hz
            if (sine_phase_rad[chan] > 2*pi):
                sine_phase_rad[chan] -= 2*pi
            val_uV += 50 * sqrt(2)*sin(sine_phase_rad[chan])  # 20 uVrms

        else:
            val_uV = 0

        val_uV *= 100
        # convert to counts, the 0.5 is to ensure rounding
        val_uV = round(0.5 + val_uV)
        byte = struct.pack(">i", val_uV)[1:]
        uVbytes.append(byte)

    return uVbytes


while True:
    now = time.time()
    chn8data = synthesizeData(freq)

    # Write to LSL
    for i in range(numChannels):
        uV[i] = int.from_bytes(chn8data[i], byteorder='big', signed=True)
    outlet.push_sample(uV)
    print(uV)
    # Time keeping for making it a true 250Hz transmission rate
    while (time.time() - now) < (1/freq):  # sleep(1/freq)
        continue
