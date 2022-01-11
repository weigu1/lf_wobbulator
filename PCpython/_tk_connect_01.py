"""
 test for upython GUI
 Unfortunately it is not possible to combine ampy and SerialTextbox, as
 they conflict on the serial port.
 
 So 2 possibilities:
 GUI for cli amply
 modify pyboard.py
 

"""    
import time
import threading, queue
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import serial 
from serial.tools import list_ports
import pico_connect_02 as pconn

import os
from terminalwindow_04 import Terminalwindow
#---------------------------------------------------------------------- 

#---------------------------------------------------------------------- 


def disconnect():
    serial_textbox.disconnect()
    
def clear():
    serial_textbox.delete('1.0', tk.END)

def send():
    #rawREPL()
    t = cmd_textbox.get('1.0', tk.END) +  "\r\n"
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

#--------------------------------------------------------------

if __name__ == "__main__":  
    
    
    from listbox_dialog import MyListbox
    
    
    comport = select_port()
     
    mainwindow = tk.Tk()
    
    serial_textbox=Terminalwindow(comport, baud , master = mainwindow)      
    serial_textbox.pack()
    serial_textbox.connect()
    
        
    b0=tk.Button(mainwindow, text="Clear", command=clear)
    b0.pack(side=tk.LEFT)
    
    b1=tk.Button(mainwindow, text="Send", command=send)
    b1.pack(side=tk.LEFT)
    
    b2=tk.Button(mainwindow, text="Raw REPL", command=rawREPL)
    b2.pack(side=tk.LEFT)
    
    b3=tk.Button(mainwindow, text="Normal REPL", command=normalREPL)
    b3.pack(side=tk.LEFT)
    
    b4=tk.Button(mainwindow, text="Stop program", command=interrupt_program)
    b4.pack(side=tk.LEFT)
    
    b5=tk.Button(mainwindow, text="Soft reset", command=soft_reset)
    b5.pack(side=tk.LEFT)
    
       
    b7 = tk.Button(mainwindow, text="listdir", command=ls)
    b7.pack()    
    
    mainwindow.mainloop()
    
