# -*- coding: utf-8 -*-

""" mcp3424.py  weigu.lu 
    lib to interfacing MCP3424 with the Pico
    MCP3424 : 4 channel 18-bit ΔΣ ADC with differential inputs    
    Self Calibration of Internal Offset and Gain per Each Conversion
    3.75 SPS (18 bits),  15 SPS (16 bits), 60 SPS (14 bits), 240 SPS (12 bits)
    Single Supply Operation: 2.7V to 5.5V
    Interface I2C (exists with 2 channel MCP3422)
    The on-board 2.048V reference voltage enables an input range of
    ± 2.048V differentially.
    Adr0 and Adr1 to GND or floating 0b000 -> 0x68
"""

__version__ = "0.3.0"
__author__ = "Guy WEILER weigu.lu"
__copyright__ = "Copyright 2022, weigu.lu"
__credits__ = ["Guy WEILER", "Jean-Claude FELTES"]
__license__ = "GPL"
__maintainer__ = "Guy WEILER"
__email__ = "weigu@weigu.lu"
__status__ = "Development" # "Prototype", "Development", or "Production"

from machine import Pin, I2C
from time import sleep

class MCP3424():
    def __init__(self, i2c_bus_nr, pin_scl, pin_sda, i2c_frequ,
                 channel=1, bits=16, gain=1, cont=1):
        """ Create MCP3424 configuration byte masks to cook config byte
            and write the byte  """
        self.MCP3424_ADDRESS = 0x68 # I2C address        
        self.i2c = I2C(i2c_bus_nr, scl=Pin(pin_scl), sda=Pin(pin_sda),
                       freq=i2c_frequ)
        if cont == 1:
            self.conv = 0x00                # Bit 7: 0 Continious
        else:
            self.conv = 0x80                # Bit 7: 1 Init conv (One-Shot Mode)
        self.channel = ((channel-1)*2)<<4   # Bits 65: 1:00 2:01 3:10 4: 11
        self.mode = cont<<4                 # Bit 4: 1 Mode continious (def)
        self.bits = (bits-12)<<1            # Bits 32: 12:00 14:01 16:10 18:11
        self.gain = gain//2                 # Bits 10: 1:00 2:01 4:10 8:11
        if self.gain == 4:
            self.gain = 3
        self.scan_i2c_bus()    
        config_byte = self.get_config_byte()
        self.send_config_byte(config_byte)
        
    def scan_i2c_bus(self):
        device_list = self.i2c.scan()    
        for devices in device_list:        
            print(hex(devices))
            if (devices & 0xF8) == self.MCP3424_ADDRESS:
                self.MCP3424_ADDRESS = devices
                print("MCP3424 detected!")
            else:
                print("Check your connections (don't forget the pull-ups)!")        
        
    def get_config_byte(self):
        """ Cook the configuration byte """
        config_byte = 0               
        config_byte = self.conv | self.channel | self.mode | \
                      self.bits | self.gain
        return config_byte
    
    def get_bits(self):
        """"""
        return ((self.bits)>>1)+12        
    
    def send_config_byte(self, config_byte):
        """ Send the Configuration byte """
        self.i2c.writeto(self.MCP3424_ADDRESS, bytearray([config_byte]))
        
    def reset(self):
        """ Reset with General call """
        self.i2c.writeto(self.MCP3424_ADDRESS, b'06')
        
    def read_adc(self):
        """ Read data from MCP3424
            12, 14 or 16 bit: 2 bytes data + config byte
            18 bit: 3 bytes data + config byte """
        config_byte = self.get_config_byte()
        data = self.i2c.readfrom(self.MCP3424_ADDRESS, 4)        
        if data[3] == config_byte:
            #print("We use 18 bit: 3.75 SPS")
            adc_value = ((data[0] & 0x03) * 65536) + (data[1] * 256) + data[2] # 18-bits
        elif data[2] & 0x0C == 0x08:
            #print("We use 16 bit: 15 SPS")
            adc_value = (data[0] * 256) + data[1] # 12-bits
        elif data[2] & 0x0C == 0x04:
            #print("We use 14 bit: 60 SPS")
            adc_value = ((data[0] & 0x3F) * 256) + data[1] # 14-bits
        elif data[2] & 0x0C == 0x00:
            #print("We use 12 bit: 240 SPS")
            adc_value = ((data[0] & 0x0F) * 256) + data[1] # 12-bits
        else:
            adc_value = -1
        voltage = adc_value/(2**self.get_bits())*4.096    
        return adc_value, voltage
    
    def read_voltage(self):        
        adc_value, voltage = self.read_adc()        
        return voltage

##############################################################################
        
def create_default_adc():
    I2C_FREQ = 400000
    I2C_BUS_NR = 0 # we use I2C0 on pin 8 and 9
    PIN_SDA = 8 
    PIN_SCL = 9
    ACD_CHANNEL = 1   # from 4
    ACD_CONT_MODE = 1 # 0 = manual mode
    ACD_BITS = 16     # 12(160sps), 14(60sps), 16(15sps), 18(3.75sps)
    ADC_GAIN = 1      # 1V/V, 2V/V, 4V/V, 8V/V
    adc = MCP3424(I2C_BUS_NR, PIN_SCL, PIN_SDA, I2C_FREQ, channel=ACD_CHANNEL,
                  bits=ACD_BITS, gain=ADC_GAIN, cont=ACD_CONT_MODE)    
    
    adc_value, voltage = adc.read_adc()
    print("ADC value: " + str(adc_value))
    print ("Voltage = " + "{:1.4f}".format(voltage) + " V")    
    return adc

##############################################################################

if __name__ == '__main__':    
    adc = create_default_adc()

  
