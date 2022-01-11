"""
  
Class Terminalwindow defines a ScrolledTextbox that is attached to a serial port
Received text  from serial port is automatically written to text box
Keys typed in the text box are directly sent to serial port
    
    Usage:
    comport="/dev/ttyUSB0"
    baud = 38400 
    serial_textbox=Terminalwindow(comport, baud )  
    serial_textbox.timeout=0.2    
    serial_textbox.pack()
    serial_textbox.filter_CR = 2       
    serial_textbox.connect()
    ....
    serial_textbox.disconnect()
    
    self.filter_CR =
            0 nothing
            1 replace '\r' with  ''   (suppress LF from CRLF)
            2 replace '\r' with '\n'
    
    All serial methods and attributes are available for Terminalwindow
"""    
comport="/dev/ttyUSB1"
comport="/dev/ttyACM0"
baud = 9600            


import threading, queue
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import serial 
import time 


from serial.tools import list_ports


    
#----------------------------------------------------------------------        
class Terminalwindow( serial.Serial, ScrolledText):
    """inherits first from Serial, then from ScrolledText
       this is a little bit dangerous as methods with the same name
       from one and the other might conflict!
       But it is rather practical if there are no conflicts
       
       self.filter_CR =
            0 nothing
            1 replace '\r' with  ''   (suppress LF from CRLF)
            2 replace '\r' with '\n'
            
    """        
    def __init__(self, COMport, baudrate, **kwargs):
        # init textbox and serial port
        ScrolledText.__init__(self, **kwargs)  
        serial.Serial.__init__(self)
       
        
        # set Serial port and baudrate
        
        self.port=COMport
        self.baudrate = baudrate 
               
        # suppress carriage return ( CRLF -> LF only)
        self.filter_CR=1
        
        # Create stop event (to terminate endless receiving loop)
        # and message queue for thread (to transmit received text to TextCtrl)
        self.stopevent=threading.Event() 
        self.msgQueue=queue.Queue()
 
        # Bindings for Key event (send to RS232)
        # and Destroy -> stop serial thread
        self.bind("<Key>", self._OnKeypress )
        self.bind("<Destroy>", self._OnDestroy  )
        
        # start polling for message in queue
        self._poll_message()
        
    def _OnDestroy(self, event):
        # on destruction, tell serial thread to stop, otherwise it stays alive
        self.disconnect()
            
        
    def _poll_message(self):
        # regularily update text from message queue 
        while not self.msgQueue.empty():
            msg=self.msgQueue.get()
            self.insert(tk.END,msg)
            self.see(tk.END)  
        # do this again every 50ms
        self.after(50, self._poll_message )
                
        

    def disconnect(self):
        # set stop event so endless receiving loop is interrupted
        self.stopevent.set()
        
    
    def connect(self):
        """connect to COM port and read characters to Terminalwindow"""
        
         # open port if not already open        
        if self.isOpen()==False:
            self.open()
        if self.isOpen():
            print("connected, port", self.portstr, "    ",self.baudrate,"baud")
        else:
            print("Could not open port ", self.portstr)
        
        self.reset_input_buffer()
        self.reset_output_buffer()
        
        
        # create a new thread object that runs serial thread
        # to read serial characters
        self.serialthread = threading.Thread(group=None, target=self._readSerial , 
            name="ser_read",args=(), kwargs={})
        # clear stopevent and start thread
        self.stopevent.clear()
        self.serialthread.start()
       
        
    def _readSerial(self):
        """ read characters of data to terminal textbox
            this runs in a separate thread  """ 
            
        # endless receiving loop
        while True:
            try:
                # read bytes and put them to message queue:
                nbbytes = self.inWaiting()
                if nbbytes >0:
                    c = self.read(nbbytes)
                    
                    ##  for Python 3 strings
                    c=c.decode("utf-8")
                    ##
                    
                    # eventually suppress CR
                    if self.filter_CR == 1:
                        c=c.replace("\r", "")
                    elif self.filter_CR == 2:
                        c=c.replace("\r", "\n")
                    self.msgQueue.put(c)
                   
            except:
                pass 
                
            # interrupt loop when stop event is set
            if self.stopevent.isSet():
                break 
                
        print("disconnected")  
        self.close()
        
    
          
        
    def _OnKeypress(self,event):
        # Respond to key press in text box
        ok = event.char
        ##  for Python 3 strings
        ok = ok.encode("utf8")
        ##
        ##self.write(ok)
              
               
        try:
            # write to port
            if self.isOpen()== True: 
                self.write(ok)
        except:
            print("PORT WRITE ERROR", end=' ')
        
               
        return "break"      # don't send key event to textbox
        
        
    def write_serial(self,s):
        """ write s to the connected serial port"""
        try:
            self.write(s)
        except:
            print("PORT ERROR")    
            
            
    def list_comports(self):
        
        p = ''
        for port in list_ports.comports():
            p += str(port.device) + '\t\t\t' + port.description + '\n'
            
        self.insert(tk.END, p)
                                      
#---------------------------------------------------------------------- 
if __name__ == "__main__":
    

    # textbox
        
    def clear():
        serial_textbox.delete('1.0', tk.END)
            
    def disconnect():
        serial_textbox.disconnect()
    
    def connect():
        serial_textbox.connect()
        
    def show_comports():
        
        serial_textbox.list_comports()    
    
    #------------------------------------------------------
    def number_to_hexbyte(n):
        s = hex(n)
        s = s[2:]
        s = bytes(s.encode('utf-8'))
        
        return s    
    
        
    def clear():
        serial_textbox.delete('1.0', tk.END)
            
    def disconnect():
        serial_textbox.disconnect()
    
    def connect():
        serial_textbox.connect()
        
    def show_comports():
        
        serial_textbox.list_comports()    
    
    #------------------------------------------------------
    def number_to_hexbyte(n):
        s = hex(n)
        s = s[2:]
        s = bytes(s.encode('utf-8'))
        
        return s    
    
    
    
    




    for port in list_ports.comports():
        print(port.device)
    
    
    mainwindow = tk.Tk()
   
   
    
    serial_textbox=Terminalwindow(comport, baud, master = mainwindow )  
    serial_textbox.timeout=0.2    
    serial_textbox.pack()
    serial_textbox.filter_CR = 2
    serial_textbox.connect()
        
    b0=tk.Button(mainwindow, text="Clear", command=clear)
    b0.pack(side=tk.LEFT)
    
        
    b4 = tk.Button(mainwindow, text="connect", command=connect) 
    b4.pack(side=tk.LEFT)   
    b5 = tk.Button(mainwindow, text="disconnect", command=disconnect) 
    b5.pack(side=tk.LEFT)  
    
    b7 = tk.Button(mainwindow, text="List ports", command=show_comports) 
    b7.pack(side=tk.LEFT)  
    
    mainwindow.mainloop()
    
