# -*- coding: utf-8 -*-

""" lf-wobbulator 
    2022-01-07
"""

__version__ = "0.0.3"
__author__ = "Guy WEILER weigu.lu"
__copyright__ = "Copyright 2022, weigu.lu"
#__credits__ = ["Guy WEILER", "Jean-Claude FELTES"]
__license__ = "GPL"
__maintainer__ = "Guy WEILER"
__email__ = "weigu@weigu.lu"
__status__ = "Prototype" # "Prototype", "Development", or "Production"

from lf_wobbulator_ini import *
from machine import Pin, SPI, I2C
from time import sleep, time
from math import log10
from ad9833 import AD9833
from mcp3424 import MCP3424
from pico_epaper_3in7 import *
import framebuf
import utime
from lf_wobb_tools import LF_Wobb_Tools

DISPLAY = 1
SD_CARD_READER = 0

def wobbulate():    
    adc = MCP3424(I2C_BUS_NR, PIN_SCL, PIN_SDA, I2C_FREQ, channel=ACD_CHANNEL,
                  bits=ACD_BITS, gain=ADC_GAIN, cont=ACD_CONT_MODE)    
    adc_config_byte = adc.get_config_byte()
    wave = AD9833(CRYSTAL_FREQ, PIN_DDS_CS, PIN_SCK, PIN_MOSI, PIN_POT_CS, POT_VALUE)
    tools = LF_Wobb_Tools()    
    pot_value = POT_VALUE # if no calibration
    max_voltage = MAX_VOLTAGE
    #pot_value, max_voltage = tools.calibrate_pot(wave, adc, MAX_VOLTAGE, CAL_FREQ, POT_START_VALUE)
    freq_list = tools.create_frequency_list(1,1000000,10) # start, stop, step
    print(freq_list)    
    ampl_volt_list = []
    
    print("frequency\tvoltage")    
    start = time()
    for fr in freq_list:
        decade = int(log10(fr))+1        
        tools.switch_cap(decade, PIN_DISCHARGE, PIN_C1, PIN_C2, PIN_C3, PIN_C4, PIN_C5)
        exp = decade-1    
        wave.set_freq(fr)
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
            voltage = adc.read_voltage()
            voltage_sum += voltage
            print(str(voltage) + '\t',end='')
        voltage = voltage_sum/NR_SAMPLES
        print("avg: " + str(voltage))
        ampl_volt_list.append(voltage)                
        print (str(fr) + '\t' + str(voltage))
        #print (str(i).replace('.',',') + ',' + str(voltage).replace('.',','))
    #print(ampl_volt_list)
    
    end = time()
    print("measering time [s]: "+ str(end - start))
    
    if DISPLAY:
        epd = EPD_3in7(PIN_DC, PIN_CS, PIN_RST, PIN_BUSY)
        buf_ls_b, buf_epaper_p_b, fb_ls_b = init_e_paper(epd)
        cook_e_paper_image(epd, HEADER, freq_list, ampl_volt_list, max_voltage, fb_ls_b)
        write_e_paper(epd, buf_ls_b, buf_epaper_p_b)

if __name__ == '__main__':
    wobbulate()

