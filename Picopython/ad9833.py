# -*- coding: utf-8 -*-

""" ad9833.py
    Interfacing AD9833 DDS breakout with the Pico
    We use the boards with digital pot MCP41010 and
    opamp AD8051
    
    VCC    - 3.3V
    GNG    - GND
    FSYNC  - GPIO5 (CS)
    SCLK   - GPIO6 (SCK)
    SDATA  - GPIO7 (MOSI)
    OUTPUT - PGA   (Programmable Gain Amp)
    
    ! we get a gain of 1+(5k/500) = 11 (one board gain= 6)
    With 0.6V (output DDS) the max of pot = 180 for Vpp=5V !
"""

__version__ = "0.2.0"
__author__ = "Guy WEILER weigu.lu"
__copyright__ = "Copyright 2022, weigu.lu"
__credits__ = ["Guy WEILER", "Jean-Claude FELTES"]
__license__ = "GPL"
__maintainer__ = "Guy WEILER"
__email__ = "weigu@weigu.lu"
__status__ = "Development" # "Prototype", "Development", or "Production"

from machine import Pin, SPI
from time import sleep

class AD9833():
    """A class to interface an AD9833 DDS chip.
       We have also methods to interface AD9833 breakout board with
       digital pot MCP41010 and opamp AD8051. If you have only the DDS chip,
       omit the two last init parameter: e.g. wave = AD9833(25000000,5,6,7)"""
  
    def __init__(self, crystal_freq, pin_dds_cs, pin_sck, pin_mosi,
                 pin_pot_cs=-1, pot_value = -1):
        """"""        
        self.crystal_freq = crystal_freq
        # init SPI
        self.spi = SPI(0,
                  baudrate = 1_000_000,
                  polarity = 1,
                  phase = 0, # DDS needs phase = 0
                  bits = 8,
                  sck = Pin(pin_sck, Pin.OUT),
                  mosi = Pin(pin_mosi, Pin.OUT),
                  miso = None,              
                 )
        self.dds_cs = Pin(pin_dds_cs, Pin.OUT)
        if pin_pot_cs != -1:
            self.pot_cs = Pin(pin_pot_cs, Pin.OUT)
            self.pot_cs.high()            
        self.dds_cs.high()
        if pot_value != -1:
            self.set_potentiometer(pot_value)        
        self.SINE = 0
        self.TRIANGLE = 2
        self.TWOE28 = 268435456 # 2**28        
        self.dds_cs.high()
        self.freq = 1
        self.reset()        
        
    def reset(self):
        """"""
        self.dds_cs.low()        
        self.spi.write(bytes([0x21, 0x00]))
        self.change_function(self.SINE)
        self.change_freq(self.freq)
        self.spi.write(bytes([0x20, 0x00])) #output on
        self.dds_cs.high()
        
    def convert_freq(self, freq):
        """"""
        freqreg = int(freq*self.TWOE28/self.crystal_freq)
        #print(hex(freqreg))
        b1 = freqreg >> 8 & 0x3f | 0x1 <<6 # LSW bit1514 = 01
        b2 = freqreg & 0xff
        b3 = freqreg >> 22 | 0x1 << 6      # MSW bit1514 = 01
        b4 = freqreg >> 14 & 0xff
        #print(hex(b1),'\t',hex(b2),'\t',hex(b3),'\t',hex(b4))
        return bytes([b1,b2,b3,b4])

    def change_freq(self, freq):
        """"""
        self.dds_cs.low()        
        #self.spi.write(bytes([0x21, 0x00]))        
        self.spi.write(self.convert_freq(freq))        
        #self.spi.write(bytes([0xC0, 0x00])) # Phase reg 0       
        self.spi.write(bytes([0x20, 0x00])) # Reset to 0
        self.dds_cs.high()        

    def change_function(self, fun):
        """ Changes output function.
            Valid values to pass to this function are:
            0 - sine
            2 - triangle
            40 - square
            32 - square (half frequency) """
        self.dds_cs.low()
        self.spi.write(bytes([0x20, fun]))
        self.dds_cs.high()
        
    def set_potentiometer(self, pot_value):
        """ Change the potentiometer value (data sheet MCP41010) """ 
        self.spi.init(phase = 1), # pot needs phase = 1
        self.pot_cs.low()
        self.spi.write(bytes([0x11,pot_value]))
        self.pot_cs.high()
        self.spi.init(phase = 0), # reset phase to zero

### MAIN #####################################################################

CRYSTAL_FREQ = 25000000  # Crystal frequency in Hz
# SPI and POT
PIN_DDS_CS = 5
PIN_SCK = 6
PIN_MOSI = 7
PIN_POT_CS = 4
POT_VALUE = 80 # max = 180, depends on board! set below calibration value

def main():
    wave = AD9833(CRYSTAL_FREQ, PIN_DDS_CS, PIN_SCK, PIN_MOSI, PIN_POT_CS, POT_VALUE)
    #wave.change_function(wave.SINE)
    wave.change_freq(1000)

if __name__ == '__main__':
    main()
