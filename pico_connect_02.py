#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial
from serial.tools import list_ports
import time 

def print_port_info():
    for port in list_ports.comports():
        print("Device: ", port.device)
        try:
            print ("vid:pid", hex(port.vid), ":", hex(port.pid))
        except:
            print ("vid:pid", port.vid, ":", port.pid)    
        print("Serial number: ", port.serial_number)
        print("hiw: ", port.hwid)
        print("name: ", port.name)
        print ("description: ", port.description)
        print ("interface: ", port.interface)
        print("location: ", port.location)
        print("manufacturer", port.manufacturer)
        print("product: ", port.product)
        print()
#----------------------------------------------------------------
def scan_for_picos(verbose = False):
    '''returns list of USB ports with Raspi Picos connected '''
    
    picos = []
    for port in list_ports.comports():
        if verbose:
            print("Checking ", port.device)
        if port.manufacturer != None:
            if "MicroPython" in port.manufacturer:
                picos.append(port.device)
    return picos
#-----------------------------------------------------------------

def get_info_pico(pico, timeout=0.5):
    '''
    Get info stored on the pico in a file info.txt
        This must contain a keyword in the first line:
        The keyword is returned  
    '''
    s=serial.Serial(pico, baudrate=115200)
    if s.isOpen()==False:
        s.open()
    
    # send commands
    s.write(b'\x03\x03')        # Interrupt eventually running program
    s.write(b'\x02')            # Normal REPL
    s.write(b'f = open("info.txt", "r")\r')
    s.write(b't = f.read()\r')
    s.write(b'f.close()\r')
    s.write(b'print(t)\r')
        
    # Receive answer (with timeout)
    text = ''
    t1 = time.time()
    while True:
        nbbytes = s.inWaiting()
        if nbbytes >0:
            c = s.read(nbbytes)
            c = c.decode("utf-8")
            text += c    
        if time.time() - t1 > timeout:
            break
    
    # Analize answer
    if 'Traceback' in text:                 # Something went wrong
        info = ''
    else:                                   # Filter interesting part    
        keyword = 'print(t)'
        pos1 = text.find(keyword)
        info = text[pos1 + len(keyword) +1:]  # keyword found behind print()
        info = info.split()[0]                # take first line only    
        info = info.strip() 
        
    return info 
#----------------------------------------------------------------------    
def find_pico(keyword, timeout = 0.5):
    '''returns port where a Pico with keyword in first line of 
    info.txt is connected'''
    for picoport in scan_for_picos():
        info = get_info_pico(picoport, timeout)
        if info == keyword:
            break
    else:
        picoport = ''        
    return picoport
#--------------------------------------------------------------------  
# General Pico communication functions

def open_pico(keyword):
    '''looks for files named info.txt on the pico 
       containing keyword
       Returns opened  Serial object of serial port where this is found'''
    pico_port = find_pico(keyword, 0.05)
    if pico_port:
        print('Found ', keyword, 'Pico on port',  pico_port)   

        ser = serial.Serial(pico_port, baudrate = 115200)
        if ser.open == False:
            ser.open()
    else:
        print(keyword + " not found")
        ser = None        
    return ser, pico_port    

def get_answer(ser, timeout=0.2, verbose = True):
    t1 = time.time()
    text = ''
    while True:
        nbbytes = ser.inWaiting()
        if nbbytes >0:
            c = ser.read(nbbytes)
            c = c.decode("utf-8")
            text += c    
        if time.time() - t1 > timeout:
            break
    if verbose:
        print('RESPONSE: ', text)
    return text
    
def init_pico(ser, timeout = 0.05):
    '''Soft reset on Pico'''
    ser.write(b'\x03\x03')
    get_answer(ser, timeout)
    

def cmd_to_pico(ser, cmd, timeout=2, verbose = True):
    '''send command to Pico
       cmd is a Python code line'''
    if verbose:
        print("CMD: ", cmd)
    ser.write(cmd.encode('utf-8') + b'\r')
    get_answer(ser, timeout)
    time.sleep(0.1)    

def reset_pico(ser):
    '''Reset Pico to restart in local mode'''
    print("Pico soft reset")
    ser.write(b'\04')
    get_answer(ser, timeout = 0.5)           

#-----------------------------------------------------------------------
def pico_scan_with_info():
    '''returns dictionnary of connected picos
       in the form {port1: info1, port2: info2 ...}'''
    d = {}
    for pico_port in scan_for_picos():
        info = get_info_pico(pico_port)
        d[pico_port] = info
    return d

def pico_scan_with_info_strlist():
    picos = pico_scan_with_info()

    s = []
    for p in picos:
        s.append (str(p) + " : " + str(picos[p]))  
    return s
          
#-----------------------------------------------------------------------            
if __name__ == "__main__":
    
    
        
    # Scan all with info:
    print("Scan with info as strlist  (for listbox)")
    s = pico_scan_with_info_strlist()
    #print(s)
    for item in s:
        print(item)
        
    print()
    print("Scan with info as dictionnary")
    d = pico_scan_with_info()
    print(d)
    
    
    keyword = 'lf_wobbulator'
    
    # find all ports with picos connected:
    picos = scan_for_picos()
    print("Picos found:")
    for pico_port in picos:
        print(pico_port)

    print()
    
    # find info on all picos connected
    print("Info on Picos:")
    for pico_port in scan_for_picos():
        info = get_info_pico(pico_port)
        print (pico_port, '  INFO:  ',   info)
        
    print()
    
    # find a special pico with keyword in info.txt
   
    print ("Find Pico with keyword %s in info.txt:"%(keyword ))
    pico_port = find_pico(keyword)
    print(pico_port)
    
    ser, picoport = open_pico(keyword)
    
