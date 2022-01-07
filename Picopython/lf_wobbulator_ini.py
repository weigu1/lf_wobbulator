# -*- coding: utf-8 -*-

""" lf-wobbulator_ini
    2022-01-07
"""


""" Constants """

CRYSTAL_FREQ = 25000000  # Crystal frequency in Hz

# POT (AD9833 breakout board)
POT_VALUE = 81 # max = 180, depends on board! set below calibration value

# ADC
NR_SAMPLES = 20
ACD_CHANNEL = 1   # from 4
ACD_CONT_MODE = 1 # 0 = manual mode
ACD_BITS = 16     # 12(160sps), 14(60sps), 16(15sps), 18(3.75sps)
ADC_GAIN = 1      # 1V/V, 2V/V, 4V/V, 8V/V
# DDS board SPI PINS
PIN_DDS_CS = 5
PIN_SCK = 6
PIN_MOSI = 7
PIN_POT_CS = 4
# I2C
I2C_FREQ = 400000
I2C_BUS_NR = 0 # we use I2C0 on pin 8 and 9
PIN_SDA = 8 
PIN_SCL = 9
# Capacitor pins
PIN_DISCHARGE = 13
PIN_C1 = 22
PIN_C2 = 21    
PIN_C3 = 20
PIN_C4 = 19    
PIN_C5 = 18
# epaper pins
PIN_DC = 2
PIN_CS = 3
PIN_RST = 11
PIN_BUSY = 10

HEADER = "lf-wobbulator by Guy WEILER and Jean-Claude FELTES"