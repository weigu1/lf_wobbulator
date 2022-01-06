# -*- coding: utf-8 -*-

""" lf_wobb_tools
    2022-01-05
"""

__version__ = "0.0.2"
__author__ = "Guy WEILER weigu.lu"
__copyright__ = "Copyright 2022, weigu.lu"
#__credits__ = ["Guy WEILER", "Jean-Claude FELTES"]
__license__ = "GPL"
__maintainer__ = "Guy WEILER"
__email__ = "weigu@weigu.lu"
__status__ = "Prototype" # "Prototype", "Development", or "Production"
    
from machine import Pin, SPI, I2C
import math
from time import sleep
from ad9833 import AD9833
from mcp3424 import MCP3424
from pico_epaper_3in7 import EPD_3in7

class LF_Wobb_Tools():
    """A class with helper functions for the lf_wobbulator"""
  
    def __init__(self):
        """"""        
        pass
        # init SPI

    def calibrate_pot(self, wave, adc, pot_value):
        """ Calibrate the potentiometer at 1Hz to get 2Vpp """
        print("Calibrating")
        adc_config_byte = adc.get_config_byte()
        wave.change_freq(1)
        pot_value = pot_value-1
        voltage = 0
        self.switch_cap(1)
        counter = 0
        while(voltage<2.04):
            pot_value += 1
            print(pot_value)
            wave.set_potentiometer(pot_value)
            sleep(1)
            adc_s_value = adc.read_adc(adc_config_byte) #dummy read
            sleep(0.1)    
            adc_s_value = 0
            for j in range(0,NR_SAMPLES):
                sleep(0.1)
                adc_s_value += adc.read_adc(adc_config_byte)
            adc_value = adc_s_value/NR_SAMPLES    
            voltage = adc_value/(2**adc.get_bits())*4.096
            print(voltage)
            counter += 1
        if counter == 1:
            print("Pot value (POT) too high!")
        else:
            print("Pot calibrated; we needed",counter-1,"trials")
        return pot_value    

    def switch_cap(self, decade):
        """        """
        if decade == 1: # 100µ        
            gnd = Pin(PIN_100U, Pin.OUT)
            gnd.low()
            Pin(PIN_10U, Pin.IN)
            Pin(PIN_1U, Pin.IN)
            Pin(PIN_100N, Pin.IN)
            Pin(PIN_10N, Pin.IN)
            Pin(PIN_DISCHARGE, Pin.IN)
        if decade == 2: # 10µ (100µ//10µ)
            gnd = Pin(PIN_10U, Pin.OUT)
            gnd.low()
            Pin(PIN_100U, Pin.IN)
            Pin(PIN_1U, Pin.IN)
            Pin(PIN_100N, Pin.IN)
            Pin(PIN_10N, Pin.IN)
            Pin(PIN_DISCHARGE, Pin.IN)
        if decade == 3: # 1µ (100µ//10µ//1µ)
            gnd = Pin(PIN_1U, Pin.OUT)
            gnd.low()
            Pin(PIN_100U, Pin.IN)
            Pin(PIN_10U, Pin.IN)
            Pin(PIN_100N, Pin.IN)
            Pin(PIN_10N, Pin.IN)        
            Pin(PIN_DISCHARGE, Pin.IN)
        if decade == 4: # 100n (100µ//10µ//1µ//100n)
            gnd = Pin(PIN_100N, Pin.OUT)
            gnd.low()
            Pin(PIN_100U, Pin.IN)
            Pin(PIN_10U, Pin.IN)
            Pin(PIN_1U, Pin.IN)
            Pin(PIN_10N, Pin.IN)        
            Pin(PIN_DISCHARGE, Pin.IN)
        if decade == 5: # 10n (100µ//10µ//1µ//100n//10n)
            gnd = Pin(PIN_10N, Pin.OUT)
            gnd.low()
            Pin(PIN_100U, Pin.IN)
            Pin(PIN_10U, Pin.IN)
            Pin(PIN_1U, Pin.IN)
            Pin(PIN_100N, Pin.IN)        
            Pin(PIN_DISCHARGE, Pin.IN)
        if decade == 6: # 1n (100µ//10µ//1µ//100n//10n//1n)        
            Pin(PIN_100U, Pin.IN)
            Pin(PIN_10U, Pin.IN)
            Pin(PIN_1U, Pin.IN)
            Pin(PIN_100N, Pin.IN)
            Pin(PIN_10N, Pin.IN)        
            Pin(PIN_DISCHARGE, Pin.IN)

### MAIN #####################################################################

CRYSTAL_FREQ = 25000000  # Crystal frequency in Hz

# SPI and POT (AD9833 breakout board)
PIN_DDS_CS = 5
PIN_SCK = 6
PIN_MOSI = 7
PIN_POT_CS = 4
POT_VALUE = 80 # max = 180, depends on board! set below calibration value
# Capacitors
PIN_10N = 18
PIN_100N = 19
PIN_1U = 20
PIN_10U = 21
PIN_100U = 22
PIN_DISCHARGE = 13
# Samples used to calculate mean value
NR_SAMPLES = 20
# I2C and ADC
I2C_FREQ = 400000
I2C_BUS_NR = 0 # we use I2C0 on pin 8 and 9
PIN_SDA = 8 
PIN_SCL = 9
ACD_CHANNEL = 1   # from 4
ACD_CONT_MODE = 1 # 0 = manual mode
ACD_BITS = 16     # 12(160sps), 14(60sps), 16(15sps), 18(3.75sps)
ADC_GAIN = 1      # 1V/V, 2V/V, 4V/V, 8V/V

def main():
    ### SETUP ###
    adc = MCP3424(I2C_BUS_NR, PIN_SCL, PIN_SDA, I2C_FREQ, channel=ACD_CHANNEL,
                  cont=ACD_CONT_MODE, bits=ACD_BITS, gain=ADC_GAIN)    
    adc_config_byte = adc.get_config_byte()
    wave = AD9833(CRYSTAL_FREQ, PIN_DDS_CS, PIN_SCK, PIN_MOSI, PIN_POT_CS, POT_VALUE)
    tools = LF_Wobb_Tools()
    pot_value = POT_VALUE # if no calibration
    pot_value = tools.calibrate_pot(wave, adc, pot_value)    
    ### MAIN ###
    freq = 1000
    decade = int(math.log10(freq))
    print("decade = " + str(decade))
    exp = decade -1
    tools.switch_cap(decade)    
    wave.change_freq(freq)
    wave.set_potentiometer(0)
    discharge = Pin(PIN_DISCHARGE, Pin.OUT)
    discharge.low()
    sleep(0.1)
    discharge = Pin(PIN_DISCHARGE, Pin.IN)
    wave.set_potentiometer(pot_value)
    sleep(5/(10**exp))
    adc_s_value = adc.read_adc(adc_config_byte) #dummy read
    sleep(0.1)    
    adc_s_value = 0
    for j in range(0,NR_SAMPLES):
        sleep(0.1)
        adc_s_value += adc.read_adc(adc_config_byte)
    adc_value = adc_s_value/NR_SAMPLES
    voltage = (adc_value/(2**adc.get_bits())*4.096)-1.09 # 1.0V is the DC offset!    
    print (str(freq) + 'Hz\t' + str(voltage) + 'V')


if __name__ == '__main__':
    main()
