# -*- coding: utf-8 -*-

""" lf-wobbulator 
    2022-01-05
"""

__version__ = "0.0.1"
__author__ = "Guy WEILER weigu.lu"
__copyright__ = "Copyright 2021, weigu.lu"
#__credits__ = ["Guy WEILER", "Jean-Claude FELTES"]
__license__ = "GPL"
__maintainer__ = "Guy WEILER"
__email__ = "weigu@weigu.lu"
__status__ = "Prototype" # "Prototype", "Development", or "Production"

    
from machine import Pin, SPI, I2C
from time import sleep
from ad9833 import AD9833
from mcp3424 import MCP3424
from pico_epaper_3in7 import EPD_3in7
import framebuf
import utime
from lf_wobb_tools import LF_Wobb_Tools

### CONSTANTS ################################################################

HEADER = "lf-wobbulator by Guy WEILER and Jean-Claude FELTES"

CRYSTAL_FREQ = 25000000  # Crystal frequency in Hz

# SPI and POT (AD9833 breakout board)
PIN_DDS_CS = 5
PIN_SCK = 6
PIN_MOSI = 7
PIN_POT_CS = 4
POT_VALUE = 82 # max = 180, depends on board! set below calibration value
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


def init_e_paper(epd): #Init the display
    """ black = 0, white = 1 """
    buf_ls_b       = bytearray(epd.height * epd.width // 8) # used by frame buffer (landscape)
    buf_epaper_p_b = bytearray(epd.height * epd.width // 8) # used on e-paper after calc. to match e-paper (portrait)
    fb_ls_b = framebuf.FrameBuffer(buf_ls_b, epd.height, epd.width, framebuf.MONO_VLSB)
    fb_ls_b.fill(epd.w)
    return buf_ls_b, buf_epaper_p_b, fb_ls_b

def cook_epaper_image(epd, fb_ls_b, header_text):    
    epd.header(55, 0, header_text, fb_ls_b, epd.b, epd.w)    
    x_axes_zero = 28
    y_axes_zero = 245
    epd.axes(x_axes_zero, y_axes_zero, fb_ls_b, epd.b, epd.w)    

def write_e_paper(epd, buf_ls_b, buf_epaper_p_b):
    print('Sending to display')
    buf_epaper_p_b = epd.rotate_landscape_2_portrait(epd.height, epd.width, buf_ls_b, buf_epaper_p_b)
    epd.EPD_3IN7_1Gray_Display(buf_epaper_p_b)
    print('Done!.......')
    #epd.Sleep()
    


### MAIN #####################################################################
def main():
    ### SETUP ###   
    adc = MCP3424(I2C_BUS_NR, PIN_SCL, PIN_SDA, I2C_FREQ, channel=ACD_CHANNEL,
                  cont=ACD_CONT_MODE, bits=ACD_BITS, gain=ADC_GAIN)    
    adc_config_byte = adc.get_config_byte()
    wave = AD9833(CRYSTAL_FREQ, PIN_DDS_CS, PIN_SCK, PIN_MOSI, PIN_POT_CS, POT_VALUE)
    tools = LF_Wobb_Tools()    
    pot_value = POT_VALUE # if no calibration
    #pot_value = tools.calibrate_pot(wave, adc, POT_VALUE) 

    print("frequency,voltage")

    ### MAINLOOP ###

    for decade in range(7,7):    
        tools.switch_cap(decade)
        exp = decade-1    
        for i in range(10**exp,10**(exp+1),10**exp):
            wave.change_freq(i)
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
            #print (str(i).replace('.',',') + ',' + str(voltage).replace('.',','))
            print (str(i) + ',' + str(voltage))
            
    #wave.spi.deinit()
    
    sleep(1)
    epd = EPD_3in7()
    b,w = 0,1
    buf_ls_b, buf_epaper_p_b, fb_ls_b = init_e_paper(epd)
    cook_epaper_image(epd, fb_ls_b, HEADER)
    write_e_paper(epd, buf_ls_b, buf_epaper_p_b)

if __name__ == '__main__':
    main()
