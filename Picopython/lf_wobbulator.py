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
from time import sleep
from math import log10
from ad9833 import AD9833
from mcp3424 import MCP3424
from pico_epaper_3in7 import *
import framebuf
import utime
from lf_wobb_tools import LF_Wobb_Tools

DISPLAY = 0

def wobbulate():    
    adc = MCP3424(I2C_BUS_NR, PIN_SCL, PIN_SDA, I2C_FREQ, channel=ACD_CHANNEL,
                  bits=ACD_BITS, gain=ADC_GAIN, cont=ACD_CONT_MODE)    
    adc_config_byte = adc.get_config_byte()
    wave = AD9833(CRYSTAL_FREQ, PIN_DDS_CS, PIN_SCK, PIN_MOSI, PIN_POT_CS, POT_VALUE)
    tools = LF_Wobb_Tools()    
    pot_value = POT_VALUE # if no calibration
    pot_value = tools.calibrate_pot(wave, adc, POT_VALUE)
    
    fr_list = tools.create_frequency_list(100,200,10) # start, stop, step
    print(fr_list)    
    print("frequency\tvoltage")    

    for fr in fr_list:
        decade = int(log10(fr))+1        
        tools.switch_cap(decade)
        exp = decade-1    
        wave.set_freq(fr)
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
        voltage = (adc_value/(2**adc.get_bits())*4.096) # 1.0V is the DC offset!
        #print (str(i).replace('.',',') + ',' + str(voltage).replace('.',','))
        print (str(fr) + '\t' + str(voltage))

    if DISPLAY:
        epd = EPD_3in7(PIN_DC, PIN_CS, PIN_RST, PIN_BUSY)
        buf_ls_b, buf_epaper_p_b, fb_ls_b = init_e_paper(epd)
        cook_epaper_image(epd, fb_ls_b, HEADER)
        write_e_paper(epd, buf_ls_b, buf_epaper_p_b)

if __name__ == '__main__':
    wobbulate()
