# -*- coding: utf-8 -*-
# *****************************************************************************
# * | File        :   Pico_ePaper-3.7.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# *----------------
# * | This version:   V1.0
# * | Date        :   2021-06-01
#
# Tweaked by Weigu.lu 2022
# Pins:
# DC - 2 
# CS - 3
# SCK - 6
# MOSI - 7
# BUSY - 10
# RST - 11 
#
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

__version__ = "0.0.1"
__author__ = "Guy WEILER weigu.lu"
__copyright__ = "Copyright 2022, weigu.lu"
__credits__ = ["Guy WEILER", "Jean-Claude FELTES"]
__license__ = "GPL"
__maintainer__ = "Guy WEILER"
__email__ = "weigu@weigu.lu"
__status__ = "Prototype" # "Prototype", "Development", or "Production"

from machine import Pin, SPI
import framebuf
import utime

# Display resolution
EPD_WIDTH       = 280
EPD_HEIGHT      = 480

EPD_3IN7_lut_1Gray_GC =[
0x2A,0x05,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#1
0x05,0x2A,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#2
0x2A,0x15,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#3
0x05,0x0A,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#4
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#5
0x00,0x02,0x03,0x0A,0x00,0x02,0x06,0x0A,0x05,0x00,#6
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#7
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#8
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#9
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#10
0x22,0x22,0x22,0x22,0x22
]

EPD_3IN7_lut_1Gray_DU =[
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#1
0x01,0x2A,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x0A,0x55,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#3
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#5
0x00,0x00,0x05,0x05,0x00,0x05,0x03,0x05,0x05,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#7
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#9
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x22,0x22,0x22,0x22,0x22
]

class EPD_3in7:
    def __init__(self,  pin_dc=8, pin_cs=9, pin_rst=12, pin_busy=13):
        self.pin_dc = Pin(pin_dc, Pin.OUT)
        self.pin_cs = Pin(pin_cs, Pin.OUT)
        self.pin_rst = Pin(pin_rst, Pin.OUT)        
        self.pin_busy = Pin(pin_busy, Pin.IN, Pin.PULL_UP)

        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        
        #self.lut_4Gray_GC = EPD_3IN7_lut_4Gray_GC
        self.lut_1Gray_GC = EPD_3IN7_lut_1Gray_GC
        self.lut_1Gray_DU = EPD_3IN7_lut_1Gray_DU
        #self.lut_1Gray_A2 = EPD_3IN7_lut_1Gray_A2
        
        self.b = 0
        self.w = 1
        self.black = 0x00        
        self.white = 0xff
        self.darkgray = 0xaa
        self.grayish = 0x55
        
        self.spi = SPI(0,
                  baudrate = 4_000_000,
                  polarity = 1,
                  phase = 1,
                  bits = 8,
                 )                

        self.buffer_1Gray = bytearray(self.height * self.width // 8)
        #self.buffer_4Gray = bytearray(self.height * self.width // 4)
        self.image1Gray = framebuf.FrameBuffer(self.buffer_1Gray, self.width, self.height, framebuf.MONO_HLSB)
        #self.image4Gray = framebuf.FrameBuffer(self.buffer_4Gray, self.width, self.height, framebuf.GS2_HMSB)
        
        #self.EPD_3IN7_4Gray_init()
        #self.EPD_3IN7_4Gray_Clear()
        self.EPD_3IN7_1Gray_init()
        self.EPD_3IN7_1Gray_Clear()
        utime.sleep_ms(500)        
        
    def width(self):
        return EPD_WIDTH
    
    def height(self):
        return EPD_HEIGHT

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.pin_rst, 0)

    # Hardware reset
    def reset(self):
        self.digital_write(self.pin_rst, 1)
        self.delay_ms(30) 
        self.digital_write(self.pin_rst, 0)
        self.delay_ms(3)
        self.digital_write(self.pin_rst, 1)
        self.delay_ms(30)   

    def send_command(self, command):
        self.digital_write(self.pin_dc, 0)
        self.digital_write(self.pin_cs, 0)
        self.spi_writebyte([command])
        self.digital_write(self.pin_cs, 1)

    def send_data(self, data):
        self.digital_write(self.pin_dc, 1)
        self.digital_write(self.pin_cs, 0)
        self.spi_writebyte([data])
        self.digital_write(self.pin_cs, 1)
        
    def ReadBusy(self):
        print("e-Paper busy")
        timeout = 0;
        while(self.digital_read(self.pin_busy) == 1 and timeout < 100):      #  0: idle, 1: busy
            self.delay_ms(100)
            timeout+=1
        self.delay_ms(200)
        if timeout >= 100:
            print("busy release because timeout reached")
        else:     
            print("e-Paper busy release")
        
    def Load_LUT(self,lut):
        self.send_command(0x32)
        for count in range(0, 105):
            if lut == 0 :
                self.send_data(self.lut_4Gray_GC[count])
            elif lut == 1 :
                self.send_data(self.lut_1Gray_GC[count])
            elif lut == 2 :
                self.send_data(self.lut_1Gray_DU[count])
            elif lut == 3 :
                self.send_data(self.lut_1Gray_A2[count])
            else:
                print("There is no such lut ")
        

    def EPD_3IN7_1Gray_init(self):
        self.reset()
        
        self.send_command(0x12)
        self.delay_ms(300)  
        
        self.send_command(0x46)
        self.send_data(0xF7)
        self.ReadBusy()
        self.send_command(0x47)
        self.send_data(0xF7)
        self.ReadBusy()

        self.send_command(0x01)   # setting gaet number
        self.send_data(0xDF)
        self.send_data(0x01)
        self.send_data(0x00)

        self.send_command(0x03)   # set gate voltage
        self.send_data(0x00)

        self.send_command(0x04)   # set source voltage
        self.send_data(0x41)
        self.send_data(0xA8)
        self.send_data(0x32)

        self.send_command(0x11)   # set data entry sequence
        self.send_data(0x03)

        self.send_command(0x3C)   # set border 
        self.send_data(0x03)

        self.send_command(0x0C)   # set booster strength
        self.send_data(0xAE)
        self.send_data(0xC7)
        self.send_data(0xC3)
        self.send_data(0xC0)
        self.send_data(0xC0)

        self.send_command(0x18)   # set internal sensor on
        self.send_data(0x80)
         
        self.send_command(0x2C)   # set vcom value
        self.send_data(0x44)

        self.send_command(0x37)   # set display option, these setting turn on previous function
        self.send_data(0x00)      # can switch 1 gray or 4 gray
        self.send_data(0xFF)
        self.send_data(0xFF)
        self.send_data(0xFF)
        self.send_data(0xFF)  
        self.send_data(0x4F)
        self.send_data(0xFF)
        self.send_data(0xFF)
        self.send_data(0xFF)
        self.send_data(0xFF)  

        self.send_command(0x44)   # setting X direction start/end position of RAM
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x17)
        self.send_data(0x01)

        self.send_command(0x45)   # setting Y direction start/end position of RAM
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0xDF)
        self.send_data(0x01)

        self.send_command(0x22)   # Display Update Control 2
        self.send_data(0xCF)
        
    def EPD_3IN7_1Gray_Clear(self):
        
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1

        self.send_command(0x4E)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_command(0x4F)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x24)
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0Xff)
        

        self.Load_LUT(1)

        self.send_command(0x20)
        self.ReadBusy()
        
    def EPD_3IN7_1Gray_Display(self,Image):
        
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1

        self.send_command(0x49)
        self.send_data(0x00)
        
        self.send_command(0x4E)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_command(0x4F)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x24)
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(Image[i + j * wide])
        

        self.Load_LUT(1)
        
        self.send_command(0x20)
        self.ReadBusy()
        
    def EPD_3IN7_1Gray_Display_Part(self,Image):
        
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1

        self.send_command(0x44)
        self.send_data(0x00)
        self.send_data(0x00)        
        self.send_data((self.width-1) & 0xff)
        self.send_data(((self.width-1)>>8) & 0x03)
        self.send_command(0x45)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data((self.height-1) & 0xff)
        self.send_data(((self.height-1)>>8) & 0x03)

        self.send_command(0x4E)   # SET_RAM_X_ADDRESS_COUNTER
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x4F)   # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(0x00)
        self.send_data(0x00)
        
        self.send_command(0x24)
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(Image[i + j * wide])

        self.Load_LUT(2)
        self.send_command(0x20)
        self.ReadBusy()        
        
    def Sleep(self):
        self.send_command(0X50)
        self.send_data(0xf7)
        self.send_command(0X02)  # power off
        self.send_command(0X07)  # deep sleep
        self.send_data(0xA5)
        
    ###  more functions ###

    def rotate_landscape_2_portrait(self, h, w, buf_landscape, buf_portrait):
        # Move frame buffer bytes to e-paper buffer to match e-paper
        # bytes oranisation. That is landscape mode to portrait mode.
        x=0; y=-1; n=0; m=0
        #x=0; y=0; n=1; m=0
        for i in range(0, w//8): # width/8
            for j in range(0, h): # height
                m = (n-x)+(n-y)*(w//8-1)
                buf_portrait[m] = buf_landscape[n]
                n +=1
            x = n+i+1
            y = n-1
        return buf_portrait    

    def header(self, x, y, header, fb_ls_b, b, w):
        '''Print the header line (white on black rectangle)'''
        margin_h = 4
        margin_v = 2
        fb_ls_b.fill_rect(x, y, (len(header)*8)+(2*margin_h), 2*margin_v+8, b)
        fb_ls_b.text(header, margin_h+x, margin_v, w)
        
    def axes(self, x_zero, y_zero, fb_ls_b, b, w):
        x_axes_margin_right = 0
        y_axes_margin_top = 10
        x_length = EPD_HEIGHT-x_zero -x_axes_margin_right #Lansdscape!
        y_length = EPD_WIDTH-(EPD_WIDTH-y_zero)-y_axes_margin_top
        y_end = y_zero-y_length
        x_end = x_zero+x_length
        # double lines for axes
        fb_ls_b.vline(x_zero, y_end, y_length, b)
        fb_ls_b.vline(x_zero-1, y_end, y_length+1, b)
        fb_ls_b.hline(x_zero, y_zero, x_length, b)
        fb_ls_b.hline(x_zero-1, y_zero+1, x_length+1, b)
        # vertical axes ticklines
        vtick_dist = 75 # = vtick text distance        
        vaxes_last_tick_offset = 15
        y_tick_end = y_end + vaxes_last_tick_offset        
        for i in range(0,3):
            fb_ls_b.hline(x_zero-3,i*vtick_dist+y_tick_end, 6, b)
        # vertical axes ticks text        
        vtick_txt_voffset = -3 # offset txt to ticks to align in the middle       
        for i in range(0,3):
            if i != 0:
                fb_ls_b.text("-", 0, i*vtick_dist+y_tick_end+vtick_txt_voffset, b)
                fb_ls_b.text(str(i), 8, i*vtick_dist+y_tick_end+vtick_txt_voffset, b)
            fb_ls_b.text("0", 16, i*vtick_dist+y_tick_end+vtick_txt_voffset, b)
        # vertical axes arrow
        fb_ls_b.line(x_zero-1-2,y_end+10,x_zero-1,y_end, b)
        fb_ls_b.line(x_zero-1+3,y_end+10,x_zero-1+1,y_end, b)
        fb_ls_b.line(x_zero-1-1,y_end+10,x_zero-1,y_end, b)
        fb_ls_b.line(x_zero-1+2,y_end+10,x_zero-1+1,y_end, b)
        # vertical axes label
        fb_ls_b.text("G/dB", 0, 0, b)
        # horizontal axes ticklines
        htick_dist = 73
        htick_offset = x_zero
        for i in range(0,7):
            fb_ls_b.vline(i*htick_dist+htick_offset, y_zero-2, 6, b)
        # horizontal axes arrow
        fb_ls_b.line(x_end-10,y_zero-2,x_end,y_zero, b)
        fb_ls_b.line(x_end-10,y_zero+3,x_end,y_zero+1, b)
        fb_ls_b.line(x_end-10,y_zero-1,x_end,y_zero, b)
        fb_ls_b.line(x_end-10,y_zero+2,x_end,y_zero+1, b)
        # horizontal axes ticks text
        htick_txt_dist = htick_dist
        htick_txt_offset_1 = htick_offset-12
        htick_txt_offset_2 = htick_txt_offset_1+16 # exp
        for i in range(0,7):    
            fb_ls_b.text(str(i), i*htick_txt_dist+htick_txt_offset_2, y_zero+10, b)
            fb_ls_b.text("10", i*htick_txt_dist+htick_txt_offset_1, y_zero+15, b)
        # horizontal axes label
        fb_ls_b.text("f/Hz", 240, 272, b)       

##############################################################################
        
def create_default_epd():
    """ We get no direct possibility to change the orientation.
        So it is necessary to use the framebuffer an copy pixel by pixel
        from one buffer to another. We use here only black and white"""
    
    HEADER = "lf-wobbulator by Guy WEILER and Jean-Claude FELTES"
    PIN_DC          = 2
    PIN_CS          = 3
    PIN_RST         = 11
    PIN_BUSY        = 10
    epd = EPD_3in7(PIN_DC, PIN_CS, PIN_RST, PIN_BUSY)
    buf_ls_b       = bytearray(epd.height * epd.width // 8) # used by frame buffer (landscape)
    buf_epaper_p_b = bytearray(epd.height * epd.width // 8) # used on e-paper after calc. to match e-paper (portrait)
    fb_ls_b = framebuf.FrameBuffer(buf_ls_b, epd.height, epd.width, framebuf.MONO_VLSB)
    fb_ls_b.fill(epd.w)    
    epd.header(55, 0, HEADER, fb_ls_b, epd.b, epd.w)    
    x_axes_zero = 28
    y_axes_zero = 245
    epd.axes(x_axes_zero, y_axes_zero, fb_ls_b, epd.b, epd.w)
    print('Sending to display')
    buf_epaper_p_b = epd.rotate_landscape_2_portrait(epd.height, epd.width, buf_ls_b, buf_epaper_p_b)
    epd.EPD_3IN7_1Gray_Display(buf_epaper_p_b)
    print('Done!.......')    
    #epd.Sleep()
    return epd
    
##############################################################################    

if __name__=='__main__':
    epd = create_default_epd() 



'''EPD_3IN7_lut_4Gray_GC =[
0x2A,0x06,0x15,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#1
0x28,0x06,0x14,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#2
0x20,0x06,0x10,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#3
0x14,0x06,0x28,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#4
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#5
0x00,0x02,0x02,0x0A,0x00,0x00,0x00,0x08,0x08,0x02,#6
0x00,0x02,0x02,0x0A,0x00,0x00,0x00,0x00,0x00,0x00,#7
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#8
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#9
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#10
0x22,0x22,0x22,0x22,0x22
]

EPD_3IN7_lut_1Gray_A2 =[
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#1
0x0A,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#2
0x05,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#3
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#4
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#5
0x00,0x00,0x03,0x05,0x00,0x00,0x00,0x00,0x00,0x00,#6
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#7
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#8
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#9
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#10
0x22,0x22,0x22,0x22,0x22
]
'''
'''    def EPD_3IN7_4Gray_init(self):
    
        self.reset()              # SWRESET

        self.send_command(0x12)
        self.delay_ms(300)   

        self.send_command(0x46)
        self.send_data(0xF7)
        self.ReadBusy()
        self.send_command(0x47)
        self.send_data(0xF7)
        self.ReadBusy()
        
        self.send_command(0x01)   # setting gaet number
        self.send_data(0xDF)
        self.send_data(0x01)
        self.send_data(0x00)

        self.send_command(0x03)   # set gate voltage
        self.send_data(0x00)

        self.send_command(0x04)   # set source voltage
        self.send_data(0x41)
        self.send_data(0xA8)
        self.send_data(0x32)

        self.send_command(0x11)   # set data entry sequence
        self.send_data(0x03)

        self.send_command(0x3C)   # set border 
        self.send_data(0x03)

        self.send_command(0x0C)   # set booster strength
        self.send_data(0xAE)
        self.send_data(0xC7)
        self.send_data(0xC3)
        self.send_data(0xC0)
        self.send_data(0xC0)  

        self.send_command(0x18)   # set internal sensor on
        self.send_data(0x80)
         
        self.send_command(0x2C)   # set vcom value
        self.send_data(0x44)

        self.send_command(0x37)   # set display option, these setting turn on previous function
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00) 
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00) 

        self.send_command(0x44)   # setting X direction start/end position of RAM
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x17)
        self.send_data(0x01)

        self.send_command(0x45)   # setting Y direction start/end position of RAM
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0xDF)
        self.send_data(0x01)

        self.send_command(0x22)   # Display Update Control 2
        self.send_data(0xCF)
'''
'''    def EPD_3IN7_4Gray_Display(self,Image):
        
        self.send_command(0x49)
        self.send_data(0x00)

        
        self.send_command(0x4E)
        self.send_data(0x00)
        self.send_data(0x00)
        
        
        self.send_command(0x4F)
        self.send_data(0x00)
        self.send_data(0x00)
        
        self.send_command(0x24)
        for i in range(0, 16800):
            temp3=0
            for j in range(0, 2):
                temp1 = Image[i*2+j]
                for k in range(0, 2):
                    temp2 = temp1&0x03 
                    if(temp2 == 0x03):
                        temp3 |= 0x01   # white
                    elif(temp2 == 0x00):
                        temp3 |= 0x00   # black
                    elif(temp2 == 0x02):
                        temp3 |= 0x01   # gray1
                    else:   # 0x01
                        temp3 |= 0x00   # gray2
                    temp3 <<= 1

                    temp1 >>= 2
                    temp2 = temp1&0x03 
                    if(temp2 == 0x03):   # white
                        temp3 |= 0x01;
                    elif(temp2 == 0x00):   # black
                        temp3 |= 0x00;
                    elif(temp2 == 0x02):
                        temp3 |= 0x01   # gray1
                    else:   # 0x01
                        temp3 |= 0x00   # gray2
                    
                    if (( j!=1 ) | ( k!=1 )):
                        temp3 <<= 1

                    temp1 >>= 2
                    
            self.send_data(temp3)
        # new  data
        self.send_command(0x4E)
        self.send_data(0x00)
        self.send_data(0x00)
         
        
        self.send_command(0x4F)
        self.send_data(0x00)
        self.send_data(0x00)
        
        self.send_command(0x26)
        for i in range(0, 16800):
            temp3=0
            for j in range(0, 2):
                temp1 = Image[i*2+j]
                for k in range(0, 2):
                    temp2 = temp1&0x03 
                    if(temp2 == 0x03):
                        temp3 |= 0x01   # white
                    elif(temp2 == 0x00):
                        temp3 |= 0x00   # black
                    elif(temp2 == 0x02):
                        temp3 |= 0x00   # gray1
                    else:   # 0x01
                        temp3 |= 0x01   # gray2
                    temp3 <<= 1

                    temp1 >>= 2
                    temp2 = temp1&0x03
                    if(temp2 == 0x03):   # white
                        temp3 |= 0x01;
                    elif(temp2 == 0x00):   # black
                        temp3 |= 0x00;
                    elif(temp2 == 0x02):
                        temp3 |= 0x00   # gray1
                    else:   # 0x01
                        temp3 |= 0x01   # gray2
                    
                    if (( j!=1 ) | ( k!=1 )):
                        temp3 <<= 1

                    temp1 >>= 2

            self.send_data(temp3)
        
        self.Load_LUT(0)
        
        self.send_command(0x22)
        self.send_data(0xC7)
        
        self.send_command(0x20)
        
        self.ReadBusy()
'''        

'''    def EPD_3IN7_4Gray_Clear(self):    
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1

        self.send_command(0x49)
        self.send_data(0x00)
        self.send_command(0x4E)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_command(0x4F)
        self.send_data(0x00)
        self.send_data(0x00)
        
        self.send_command(0x24)
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0Xff)
        
        self.send_command(0x4E)
        self.send_data(0x00)
        self.send_data(0x00)
         
        self.send_command(0x4F)
        self.send_data(0x00)
        self.send_data(0x00)
        
        self.send_command(0x26)
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0Xff)
          
        self.Load_LUT(0)
        self.send_command(0x22)
        self.send_data(0xC7)

        self.send_command(0x20)
        self.ReadBusy()    
'''        

'''    epd.image1Gray.fill(0xff)
    epd.image4Gray.fill(0xff)
    
    epd.image4Gray.text("Waveshare", 5, 10, epd.black)
    epd.image4Gray.text("Pico_ePaper-3.7", 5, 40, epd.black)
    epd.image4Gray.text("Raspberry Pico", 5, 70, epd.black)
    epd.EPD_3IN7_4Gray_Display(epd.buffer_4Gray)
    epd.delay_ms(500)
    
    epd.image4Gray.vline(10, 90, 60, epd.black)
    epd.image4Gray.vline(90, 90, 60, epd.black)
    epd.image4Gray.hline(10, 90, 80, epd.black)
    epd.image4Gray.hline(10, 150, 80, epd.black)
    epd.image4Gray.line(10, 90, 90, 150, epd.black)
    epd.image4Gray.line(90, 90, 10, 150, epd.black)
    epd.EPD_3IN7_4Gray_Display(epd.buffer_4Gray)
    epd.delay_ms(500)
    
    epd.image4Gray.rect(10, 180, 50, 80, epd.black)
    epd.image4Gray.fill_rect(70, 180, 50, 80, epd.black)
    epd.EPD_3IN7_4Gray_Display(epd.buffer_4Gray)
    epd.delay_ms(500)
   
    epd.image4Gray.fill_rect(0, 270, 280, 30, epd.black)
    epd.image4Gray.text('GRAY1 with black background',5, 281, epd.white)
    epd.image4Gray.text('GRAY2 with white background',5, 311, epd.grayish)
    epd.image4Gray.text('GRAY3 with white background',5, 341, epd.darkgray)
    epd.image4Gray.text('GRAY4 with white background',5, 371, epd.black)
    epd.EPD_3IN7_4Gray_Display(epd.buffer_4Gray)
    epd.delay_ms(500)
    
    epd.EPD_3IN7_1Gray_init()
    for i in range(0, 10):
        epd.image1Gray.fill_rect(0, 430, 280, 10, epd.white)
        epd.image1Gray.text(str(i), 136, 431, epd.black)
        epd.EPD_3IN7_1Gray_Display_Part(epd.buffer_1Gray)

    epd.Sleep()
'''

