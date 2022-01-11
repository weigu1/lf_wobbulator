"""
 GUI for wobbulator (test)
 

"""  
from pico_connect import find_pico
#from pico_connect import scan_for_picos, find_pico, open_pico,  init_pico, cmd_to_pico, reset_pico
from serial import Serial
import time
  

#import threading, queue
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
#import serial 
#from serial.tools import list_ports
import pico_connect_02 as pconn

import os
from terminalwindow_04 import Terminalwindow
#---------------------------------------------------------------------- 


# General Pico

def disconnect():
    serial_textbox.disconnect()
    
def clear():
    serial_textbox.delete('1.0', tk.END)

def send(cmd):
    #rawREPL()
    t = cmd +  "\r\n"
    for line in t.splitlines():
        line = line + '\n'
        serial_textbox.write(line.encode("utf8")) 
        serial_textbox.write(b'\x0D\x0A') 
    #normalREPL()     
    
def rawREPL():
    # Ctrl - A
    serial_textbox.write(b'\x01')     
    
def normalREPL():
    # Ctrl - B
    serial_textbox.write(b'\x02') 
    
def interrupt_program():
    # Ctrl - C
    serial_textbox.write(b'\x03\x03')
    
def soft_reset():
    # Ctrl - D
    serial_textbox.write(b'\x04')                          
    
def paste_mode():
    # Ctrl - E
    serial_textbox.write(b'\x05')    
    

def ls():
    serial_textbox.write("import os".encode("utf8"))
    serial_textbox.write(b'\x0D\x0A')
    serial_textbox.write("os.listdir()".encode("utf8") )
    serial_textbox.write(b'\x0D\x0A')
    #cmd_textbox.insert(tk.END, "import os\n")
    #cmd_textbox.insert(tk.END, "os.listdir()\n")
    
#-------------------------------------------------------
import subprocess

def myrun(cmd):
    """from http://blog.kagesenshi.org/2008/02/teeing-python-subprocesspopen-output.html
    """
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #stdout = []
    stdout="\n"
    while True:
        line = p.stdout.readline()
        line = line.decode('utf-8')
        #stdout.append(line)
        stdout += line   
        ##print (line,)
        if line == '' and p.poll() != None:
            break
    #return ''.join(stdout)       
    return stdout 
    
#---------------------------------------------------- 

baud = 115200 
delay = 0 
   
    
def select_port():
    picos = pconn.pico_scan_with_info_strlist()
    print("Picos found:")

    for p in picos:
        print (p)

    pico = MyListbox("Picos found:", picos)
    print(pico)
    
    pico = pico.split(":")
    comport = pico[0].strip()
    return comport


# Specific wobbulator functions
    
def set_frequency(f):
    send("wave.set_freq(" + str(f) + ")" )
    
    
def init_modules():
    interrupt_program()
    
    send("from ad9833  import *")
    time.sleep(0.2)
    
    send("wave = create_default_wave()")  
    time.sleep(0.1)
    

def close_pico():
    reset_pico(ser)
    ser.close()

#---------------------------------------------------------------------- 
def set_freq():
    f = float(txtfreq.get())
    set_frequency(f)

def set_f(event):
    set_freq()
#--------------------------------------------------------------

if __name__ == "__main__":  
    
    
    comport = find_pico('lf_wobbulator')
        
     
    mainwindow = tk.Tk()
    
    serial_textbox=Terminalwindow(comport, baud , master = mainwindow)      
    serial_textbox.pack()
    serial_textbox.connect()
    
    
    init_modules()
    
    frmfreq = tk.Frame()
    lbl = tk.Label(frmfreq, text = "f/Hz: ")
    lbl.pack(side = tk.LEFT)
    txtfreq = tk.Entry(frmfreq)
    txtfreq.insert(0, "440")
    txtfreq.pack(side = tk.LEFT)
    btnfreq = tk.Button(frmfreq, text = "Set", command = set_freq)
    btnfreq.pack(side = tk.LEFT)
    frmfreq.pack()
    
        
    b0=tk.Button(mainwindow, text="Clear", command=clear)
    b0.pack(side=tk.LEFT)
    
    '''
    b1=tk.Button(mainwindow, text="Send", command=send)
    b1.pack(side=tk.LEFT)
    '''
    b2=tk.Button(mainwindow, text="Raw REPL", command=rawREPL)
    b2.pack(side=tk.LEFT)
    
    b3=tk.Button(mainwindow, text="Normal REPL", command=normalREPL)
    b3.pack(side=tk.LEFT)
    
    b4=tk.Button(mainwindow, text="Stop program", command=interrupt_program)
    b4.pack(side=tk.LEFT)
    
    b5=tk.Button(mainwindow, text="Soft reset", command=soft_reset)
    b5.pack(side=tk.LEFT)
    
    b6=tk.Button(mainwindow, text="Init modules\n (-> wave)", command=init_modules)
    b6.pack(side=tk.LEFT)
       
    b7 = tk.Button(mainwindow, text="listdir", command=ls)
    b7.pack()    
    
    txtfreq.bind("<Enter>", set_f)
    
    mainwindow.mainloop()
    
