"""
 GUI for wobbulator (test)
 

"""  
from serial import Serial
import time
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from terminalwindow_04 import Terminalwindow
from pico_connect import find_pico, scan_for_picos, get_info_pico
from buttonbar import LabeledButtonbar

baud = 115200 
delay = 0 

print("Picos found:")
for pico_port in scan_for_picos():
    info = get_info_pico(pico_port)
    print (pico_port, '  INFO:  ',   info) 


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
    
    
#---------------------------------------------------- 
   
'''    
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

'''

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
    
def mult_10():
    f = float(txtfreq.get())
    f = f * 10
    set_frequency(f)
    txtfreq.delete(0, tk.END)
    txtfreq.insert(0, str(f))    
    
def div_10():
    f = float(txtfreq.get())
    f = f / 10
    set_frequency(f)
    txtfreq.delete(0, tk.END)
    txtfreq.insert(0, str(f))    
    
#--------------------------------------------------------------

cmds1 = { '/10' : div_10,
          '*10'  : mult_10,
        }  
            

cmds2 = {    'Clear': clear,
            'Raw REPL': rawREPL,
            'Normal REPL': normalREPL,
            'Stop program': interrupt_program,
            'Soft reset': soft_reset,
            'Init wave': init_modules,
            'List DIR': ls,
        }    

if __name__ == "__main__":  
    
    
    comport = find_pico('lf_wobbulator')
        
     
    mainwindow = tk.Tk()
    
    # Frequency entry
    frmfreq = tk.Frame()
    lbl = tk.Label(frmfreq, text = "f/Hz: ")
    lbl.pack(side = tk.LEFT)
    txtfreq = tk.Entry(frmfreq)
    txtfreq.insert(0, "440")
    txtfreq.pack(side = tk.LEFT)
    btnfreq = tk.Button(frmfreq, text = "Set", command = set_freq)
    btnfreq.pack(side = tk.LEFT)
    frmfreq.pack()
    
    # Frequency manipulate buttons
    b1 = LabeledButtonbar( cmds1, "Manipulate frequency:", labelside=tk.TOP, buttonside=tk.LEFT)
    b1.config(relief=tk.RIDGE, bd=3)
    b1.pack()
    
        
    
    serial_textbox=Terminalwindow(comport, baud , master = mainwindow)      
    serial_textbox.pack()
    serial_textbox.connect()
    
    # General buttons
    b2 = LabeledButtonbar( cmds2, "Pico communicate:", labelside=tk.TOP, buttonside=tk.LEFT)
    b2.config(relief=tk.RIDGE, bd=3)
    b2.pack()
    
    init_modules()
    
    #txtfreq.bind("<Enter>", set_f)       is extremely slow. Why ????
    
    mainwindow.mainloop()
    
