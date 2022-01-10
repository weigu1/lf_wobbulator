from pico_connect import scan_for_picos, find_pico, open_pico,  init_pico, cmd_to_pico, reset_pico
from serial import Serial
import time


#-----------------------------------------------------

# Specific wobbulator functions
    
def set_frequency(f):
    cmd_to_pico(ser, "wave.set_freq(" + str(f) + ")" )
    
    
def init_modules():
    ser = open_pico("lf_wobbulator")
    time.sleep(0.1)
    init_pico(ser)
    time.sleep(0.1)
    cmd_to_pico(ser, "from ad9833  import *")
    time.sleep(0.2)
    
    cmd_to_pico(ser, "wave = create_default_wave()")  
    time.sleep(0.1)
    return ser

def close_pico():
    reset_pico(ser)
    ser.close()

    
if __name__ == "__main__":  
    
    ser = init_modules()
    
    
    ''' 
    for i in range(1,3):
        f = i * 100
        set_frequency(f)
        time.sleep(0.01)
    '''
    #set_frequency(1000)
    
    while True:
        f = float(input("Frequency/Hz: "))
        if f == 0:
            break
        set_frequency(f)
    
    
    
    close_pico()
    
"""
Micropy commands:
from ad9833 import *
>>> wave = create_default_wave()    
>>> wave.set_freq(100)
"""
