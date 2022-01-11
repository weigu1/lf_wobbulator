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
from math import log10
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

    def calibrate_pot(self, wave, adc, max_voltage = 1.8, cal_freq = 1000, pot_start_value = 70):
        """ Calibrate the potentiometer at 1Hz to get 2Vpp """
        print("Calibrating")
        NR_SAMPLES = 20
        adc_config_byte = adc.get_config_byte()
        wave.set_freq(cal_freq)
        pot_value = pot_start_value-1
        voltage = 0        
        self.switch_cap(log10(cal_freq)+1)
        counter = 0
        while(voltage<max_voltage):
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
        return pot_value, voltage    

    def switch_cap(self, decade, pin_discharge = 13, pin_C1 = 12, pin_C2 = 21, pin_C3 = 20, pin_C4 = 19, pin_C5 = 18):
        """        """
        if decade == 1: # 100µ        
            gnd = Pin(pin_C1, Pin.OUT)
            gnd.low()
            Pin(pin_C2, Pin.IN)
            Pin(pin_C3, Pin.IN)
            Pin(pin_C4, Pin.IN)
            Pin(pin_C5, Pin.IN)
            Pin(pin_discharge, Pin.IN)
        if decade == 2: # 10µ (100µ//10µ)
            gnd = Pin(pin_C2, Pin.OUT)
            gnd.low()
            Pin(pin_C1, Pin.IN)
            Pin(pin_C3, Pin.IN)
            Pin(pin_C4, Pin.IN)
            Pin(pin_C5, Pin.IN)
            Pin(pin_discharge, Pin.IN)
        if decade == 3: # 1µ (100µ//10µ//1µ)
            gnd = Pin(pin_C3, Pin.OUT)
            gnd.low()
            Pin(pin_C1, Pin.IN)
            Pin(pin_C2, Pin.IN)
            Pin(pin_C4, Pin.IN)
            Pin(pin_C5, Pin.IN)        
            Pin(pin_discharge, Pin.IN)
        if decade == 4: # 100n (100µ//10µ//1µ//100n)
            gnd = Pin(pin_C4, Pin.OUT)
            gnd.low()
            Pin(pin_C1, Pin.IN)
            Pin(pin_C2, Pin.IN)
            Pin(pin_C3, Pin.IN)
            Pin(pin_C5, Pin.IN)        
            Pin(pin_discharge, Pin.IN)
        if decade == 5: # 10n (100µ//10µ//1µ//100n//10n)
            gnd = Pin(pin_C5, Pin.OUT)
            gnd.low()
            Pin(pin_C1, Pin.IN)
            Pin(pin_C2, Pin.IN)
            Pin(pin_C3, Pin.IN)
            Pin(pin_C4, Pin.IN)        
            Pin(pin_discharge, Pin.IN)
        if decade == 6: # 1n (100µ//10µ//1µ//100n//10n//1n)        
            Pin(pin_C1, Pin.IN)
            Pin(pin_C2, Pin.IN)
            Pin(pin_C3, Pin.IN)
            Pin(pin_C4, Pin.IN)
            Pin(pin_C5, Pin.IN)        
            Pin(pin_discharge, Pin.IN)
            
    def create_frequency_list(self, start_freq, stop_freq, steps_per_decade):
        """ The frequencies must be in the range between 1Hz and 1MHz """
        start_decade = int(log10(start_freq))+1
        stop_decade = int(log10(stop_freq))+1        
        freq_list = [start_freq]
        if start_decade != stop_decade:
            # from freq_start to end first decade
            freq_step_1 = 10**start_decade//steps_per_decade
            #print(freq_step_1)
            for i in range(10**(start_decade-1),10**start_decade,freq_step_1):
                if start_freq < i:
                    freq_list.append(i)
            decades_between = stop_decade-start_decade-1
            #print(decades_between)
            for j in range(0,decades_between):
                freq_step_b = 10**(start_decade+j+1)//steps_per_decade                
                for i in range(10**(start_decade+j),10**(start_decade+j+1),freq_step_b):            
                    freq_list.append(i)
            freq_step_3 = 10**stop_decade//steps_per_decade    
            #print(freq_step_3)
            for i in range(10**(stop_decade-1),10**stop_decade,freq_step_3):
                if stop_freq > i:
                    freq_list.append(i)
            freq_list.append(stop_freq)
        else:
            freq_step = 10**start_decade//steps_per_decade
            for i in range(10**(start_decade-1),10**start_decade,freq_step):
                if start_freq < i and stop_freq > i:
                    freq_list.append(i)
            freq_list.append(stop_freq)        
        return freq_list

            

##############################################################################
        
def create_default_wobb():
    CRYSTAL_FREQ = 25000000  # Crystal frequency in Hz
    # SPI and POT (AD9833 breakout board)
    PIN_DDS_CS = 5
    PIN_SCK = 6
    PIN_MOSI = 7
    PIN_POT_CS = 4
    POT_VALUE = 80 # max = 180, depends on board! set below calibration value
    # Capacitors
    PIN_DISCHARGE = 13
    PIN_C1 = 22
    PIN_C2 = 21    
    PIN_C3 = 20
    PIN_C4 = 19    
    PIN_C5 = 18
    # Samples used to calculate mean value
    NR_SAMPLES = 3
    # I2C and ADC
    I2C_FREQ = 400000
    I2C_BUS_NR = 0 # we use I2C0 on pin 8 and 9
    PIN_SDA = 8 
    PIN_SCL = 9
    ACD_CHANNEL = 1   # from 4
    ACD_CONT_MODE = 1 # 0 = manual mode
    ACD_BITS = 16     # 12(160sps), 14(60sps), 16(15sps), 18(3.75sps)
    ADC_GAIN = 1      # 1V/V, 2V/V, 4V/V, 8V/V
    ### SETUP ###
    adc = MCP3424(I2C_BUS_NR, PIN_SCL, PIN_SDA, I2C_FREQ, channel=ACD_CHANNEL,
                  bits=ACD_BITS, gain=ADC_GAIN, cont=ACD_CONT_MODE)    
    adc_config_byte = adc.get_config_byte()
    wave = AD9833(CRYSTAL_FREQ, PIN_DDS_CS, PIN_SCK, PIN_MOSI, PIN_POT_CS, POT_VALUE)
    tools = LF_Wobb_Tools()
    pot_value = POT_VALUE # if no calibration
    pot_value = 77 # if no calibration
    max_voltage = 1.8
    #pot_value, max_voltage = tools.calibrate_pot(wave, adc)    
    ### MAIN ###
    freq = 1000
    decade = int(log10(freq))+1
    #print("decade = " + str(decade))
    exp = decade -1
    tools.switch_cap(decade, PIN_DISCHARGE, PIN_C1, PIN_C2, PIN_C3, PIN_C4, PIN_C5)    
    wave.set_freq(freq)
    wave.set_potentiometer(0)
    discharge = Pin(PIN_DISCHARGE, Pin.OUT)
    discharge.low()
    sleep(0.1)
    discharge = Pin(PIN_DISCHARGE, Pin.IN)
    wave.set_potentiometer(pot_value)
    sleep(5/(10**exp))
    voltage = adc.read_voltage() #dummy read
    sleep(0.1)    
    voltage_sum = 0
    for j in range(0,NR_SAMPLES):
        sleep(0.1)
        voltage_sum += adc.read_voltage()
    voltage = voltage_sum/NR_SAMPLES    
    print (str(freq) + 'Hz\t' + str(voltage) + 'V')
    return wave, adc 

##############################################################################

if __name__ == '__main__':
    wave, adc = create_default_wobb()
