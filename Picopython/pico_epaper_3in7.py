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

__version__ = "0.4.0"
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
from math import log10

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

    def draw_header(self, img, header, fb_ls_b):
        '''Print the header line (white on black rectangle)'''        
        fb_ls_b.fill_rect(img["header_x"], img["header_y"], (len(header)*8)+(2*img["header_h_margin"]),
                          2*img["header_v_margin"]+8, img["b"])
        fb_ls_b.text(header, img["header_h_margin"]+img["header_x"], img["header_v_margin"], img["w"])
        
    def draw_axes(self, img, fb_ls_b):        
        # double lines for axes
        fb_ls_b.vline(img["x_axes_zero"], img["y_axis_end"], img["y_axis_length"], img["b"])
        fb_ls_b.vline(img["x_axes_zero"]-1, img["y_axis_end"], img["y_axis_length"]+1, img["b"])
        fb_ls_b.hline(img["x_axes_zero"], img["y_axes_zero"], img["x_axis_length"], img["b"])
        fb_ls_b.hline(img["x_axes_zero"]-1, img["y_axes_zero"]+1, img["x_axis_length"]+1, img["b"])
        # vertical axes ticklines                
        for i in range(0,img["y_axis_tick_number"]):
            fb_ls_b.hline(img["x_axes_zero"]-3,i*img["y_axis_tick_dist"]+img["y_axis_tick_end_top"], 6, img["b"])
        # vertical axes ticks text               
        for i in range(0,img["y_axis_tick_number"]):
            if i != 0:
                fb_ls_b.text("-", 0, i*img["y_axis_tick_dist"]+img["y_axis_tick_end_top"]+img["y_axis_tick_txt_offset"], img["b"])
                fb_ls_b.text(str(i), 8, i*img["y_axis_tick_dist"]+img["y_axis_tick_end_top"]+img["y_axis_tick_txt_offset"], img["b"])
            fb_ls_b.text("0", 16, i*img["y_axis_tick_dist"]+img["y_axis_tick_end_top"]+img["y_axis_tick_txt_offset"], img["b"])
        # vertical axes arrow
        fb_ls_b.line(img["x_axes_zero"]-1-2,img["y_axis_end"]+10,img["x_axes_zero"]-1,img["y_axis_end"], img["b"])
        fb_ls_b.line(img["x_axes_zero"]-1+3,img["y_axis_end"]+10,img["x_axes_zero"]-1+1,img["y_axis_end"], img["b"])
        fb_ls_b.line(img["x_axes_zero"]-1-1,img["y_axis_end"]+10,img["x_axes_zero"]-1,img["y_axis_end"], img["b"])
        fb_ls_b.line(img["x_axes_zero"]-1+2,img["y_axis_end"]+10,img["x_axes_zero"]-1+1,img["y_axis_end"], img["b"])
        # vertical axes label
        fb_ls_b.text("G/dB", 0, 0, img["b"])
        # horizontal axes ticklines
        for i in range(0,img["x_axis_tick_number"]):
            fb_ls_b.vline(i*img["x_axis_tick_dist"]+img["x_axis_tick_offset"], img["y_axes_zero"]-2, 6, img["b"])
        # horizontal axes arrow
        fb_ls_b.line(img["x_axis_end"]-10,img["y_axes_zero"]-2,img["x_axis_end"],img["y_axes_zero"], img["b"])
        fb_ls_b.line(img["x_axis_end"]-10,img["y_axes_zero"]+3,img["x_axis_end"],img["y_axes_zero"]+1, img["b"])
        fb_ls_b.line(img["x_axis_end"]-10,img["y_axes_zero"]-1,img["x_axis_end"],img["y_axes_zero"], img["b"])
        fb_ls_b.line(img["x_axis_end"]-10,img["y_axes_zero"]+2,img["x_axis_end"],img["y_axes_zero"]+1, img["b"])
        # horizontal axes ticks text        
        for i in range(0,img["x_axis_tick_number"]):    
            fb_ls_b.text(str(i), i*img["x_axis_tick_dist"]+img["x_axis_tick_txt_offset_2"], img["y_axes_zero"]+10, img["b"])
            fb_ls_b.text("10", i*img["x_axis_tick_dist"]+img["x_axis_tick_txt_offset_1"], img["y_axes_zero"]+15, img["b"])
        # horizontal axes label
        fb_ls_b.text("f/Hz", 240, 272, img["b"])
        
    def draw_grid_crosses(self, img, fb_ls_b):        
        for j in range(0,img["y_axis_tick_number"]):            
            for i in range(0,img["x_axis_tick_number"]):
                fb_ls_b.vline(i*img["x_axis_tick_dist"]+img["x_axis_tick_offset"],
                              j*img["y_axis_tick_dist"]+img["y_axis_tick_end_top"]-img["grid_cross_length"]//2,
                              img["grid_cross_length"], img["b"])
                fb_ls_b.hline(i*img["x_axis_tick_dist"]+img["x_axis_tick_offset"]-img["grid_cross_length"]//2,
                              j*img["y_axis_tick_dist"]+img["y_axis_tick_end_top"], img["grid_cross_length"], img["b"])
    def draw_3db_line(self, img, fb_ls_b):
        y_3db = img["y_axes_margin_top"]+img["y_axis_last_tick_offset"]+3*img["y_axis_tick_dist"]//10
        y_3db_txt_offset = 8
        fb_ls_b.hline(img["x_axes_zero"]-3,y_3db, 6, img["b"])        
        fb_ls_b.text("-3", y_3db_txt_offset, y_3db+img["y_axis_tick_txt_offset"], img["b"])
        
        for x in range(img["x_axes_zero"],img["x_axes_zero"]+img["x_axis_length"]):            
            if x%2==0:                
                fb_ls_b.vline(x, y_3db, 1, img["b"])
                #img["y_tick_end"]+10

    def draw_data_points(self, img, freq_list, ampl_list, ref_voltage, fb_ls_b):        
        img["x_axis_tick_dist"] = 73        
        x_old = img["x_axes_zero"]
        y_old = 25
        for i in range(0,len(freq_list)):
            x = int(img["x_axes_zero"] + (log10(freq_list[i])*img["x_axis_tick_dist"]))            
            G = ampl_list[i]/ref_voltage
            Gdb = 20*log10(G)            
            y = int(25-Gdb*img["y_axis_tick_dist"]/10)            
            fb_ls_b.line(x_old, y_old, x, y, img["b"])
            x_old = x
            y_old = y            

##############################################################################

def init_e_paper(epd): #Init the display
    """ black = 0, white = 1 """
    buf_ls_b       = bytearray(epd.height * epd.width // 8) # used by frame buffer (landscape)
    buf_epaper_p_b = bytearray(epd.height * epd.width // 8) # used on e-paper after calc. to match e-paper (portrait)
    fb_ls_b = framebuf.FrameBuffer(buf_ls_b, epd.height, epd.width, framebuf.MONO_VLSB)
    fb_ls_b.fill(epd.w)
    return buf_ls_b, buf_epaper_p_b, fb_ls_b

def cook_e_paper_image(epd, header_text, freq_list, ampl_list, max_voltage, fb_ls_b):
    img = {"b":0,"w":1,"header_x":55, "header_y":0,"header_h_margin":4,"header_v_margin":2,
           "x_axes_zero":28,"y_axes_zero":245, "x_axes_margin_right":0,"y_axes_margin_top":10,
           "y_axis_tick_dist":40, "y_axis_tick_number":6, "y_axis_last_tick_offset":15,
           "y_axis_tick_txt_offset":-3, "x_axis_tick_dist":73,"x_axis_tick_number":7,
           "grid_cross_length":5,
          }    
    img["x_axis_length"] = EPD_HEIGHT-img["x_axes_zero"] -img["x_axes_margin_right"] #Lansdscape!
    img["y_axis_length"] = EPD_WIDTH-(EPD_WIDTH-img["y_axes_zero"])-img["y_axes_margin_top"]
    img["x_axis_end"] = img["x_axes_zero"]+img["x_axis_length"]
    img["y_axis_end"] = img["y_axes_zero"]-img["y_axis_length"]
    img["y_axis_tick_end_top"] = img["y_axis_end"] + img["y_axis_last_tick_offset"]
    img["x_axis_tick_offset"] = img["x_axes_zero"]            
    img["x_axis_tick_txt_offset_1"] = img["x_axis_tick_offset"]-12
    img["x_axis_tick_txt_offset_2"] = img["x_axis_tick_txt_offset_1"]+16 # exp

    epd.draw_header(img, header_text, fb_ls_b)    
    epd.draw_axes(img, fb_ls_b)
    epd.draw_3db_line(img, fb_ls_b)
    epd.draw_grid_crosses(img, fb_ls_b)
    epd.draw_data_points(img, freq_list, ampl_list, max_voltage, fb_ls_b)
    
def write_e_paper(epd, buf_ls_b, buf_epaper_p_b):
    print('Sending to display')
    buf_epaper_p_b = epd.rotate_landscape_2_portrait(epd.height, epd.width, buf_ls_b, buf_epaper_p_b)
    epd.EPD_3IN7_1Gray_Display(buf_epaper_p_b)
    print('Done!.......')
    #epd.Sleep()

def create_default_epd():
    """ We get no direct possibility to change the orientation.
        So it is necessary to use the framebuffer an copy pixel by pixel
        from one buffer to another. We use here only black and white"""
    
    HEADER = "lf-wobbulator by Guy WEILER and Jean-Claude FELTES"
    PIN_DC          = 2
    PIN_CS          = 3
    PIN_RST         = 11
    PIN_BUSY        = 10
    dummy_freq_list = [10,100,1000,10000,100000,1000000]
    dummy_ampl_list = [1.8,2,1,0.1,0.01,0.1]
    epd = EPD_3in7(PIN_DC, PIN_CS, PIN_RST, PIN_BUSY)
    buf_ls_b, buf_epaper_p_b, fb_ls_b = init_e_paper(epd)
    cook_e_paper_image(epd, HEADER, dummy_freq_list, dummy_ampl_list, fb_ls_b) 
    write_e_paper(epd, buf_ls_b, buf_epaper_p_b)
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

