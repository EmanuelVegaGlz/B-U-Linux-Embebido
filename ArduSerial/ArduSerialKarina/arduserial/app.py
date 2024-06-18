from tkinter import Button
from tkinter import Frame
from tkinter import Label
from tkinter import Tk
from tkinter.ttk import Combobox

from sensor_serial import BAUDRATES
from sensor_serial import SensorSerial
from utils import find_available_serial_ports

class App(Frame):

    def __init__(self, master, *args, **kwargs)-> None:
        Frame.__init__(self, master, *args, **kwargs)
        self.master: Tk = master
        # GUI objects creations
        self.serial_devices_combobox: Combobox = self.create_serial_devices_combobox()
        self.refresh_serial_devices_button : Button = self.create_serial_devices_refresh_button()
        self.baudrate_combobox : Combobox = self.create_baudrate_combobox()
        self.connect_serial_button: Button = self.create_connect_serial_button()
        self.temperature_label: Label = self.create_temperature_label()
        self.read_temperature_button: Button = self.create_read_temperature_button()
        # Other objects
        self.sensor_serial : SensorSerial
        self.init_gui()
    
    def init_gui(self,)-> None:
        # GUI Config
        self.master.title = 'example'
        self.master.geometry('1200x800')
        self['bg'] = 'white'
        self.pack(fill='both', expand=True)

        # Row 0 
        self.serial_devices_combobox.grid(row=0, column=0, padx=10, pady=5)
        self.refresh_serial_devices_button.grid(row=1, column=0, padx=10, pady=5)
        self.baudrate_combobox.grid(row=0, column=2, padx=10, pady=5)
        self.connect_serial_button.grid(row=1, column=2, padx=10, pady=5)
        # Row 1
        self.temperature_label.grid(row=2, column=3, padx=10, pady=5)
        # Row 2 (Buttons moved here)
        self.read_temperature_button.grid(row=3, column=3, padx=10, pady=5)
        #settings
        self.baudrate_combobox.current(0) 
    
    def create_serial_devices_combobox(self)-> Combobox:
        ports = find_available_serial_ports()
        return Combobox(
            self, 
            values=ports, 
               font=("Arial", 12),  
        )
    
    def create_serial_devices_refresh_button(self) -> Button:
        return Button(
            self, 
            text='Refresh available serial devices', 
            command=self.refresh_serial_devices, 
            bg="LightSteelBlue4",
            fg="black",
            font=("Arial", 9),    
            width=25
        )   

    
    def create_baudrate_combobox(self,) -> Combobox:
        return Combobox(
            master=self,
            values=['Baudrate'] + BAUDRATES,
                font=("Arial", 12),  
        )
    
    def create_connect_serial_button(self) -> Button:
        return Button(
            master=self,
            text='Connect',
            command=self.create_sensor_serial,
             bg="LavenderBlush2",
            fg="black",
            font=("Arial", 9),    
            width=20
        )
    
    def create_temperature_label(self)-> Label:
        return Label(
            master=self,
            text= 'XX ºC',
           font=("Arial", 12),          )
    
    def create_read_temperature_button(self)->Button:
        return Button(
            master=self, 
            text='Read Temperature',
            command=self.read_temperature,
             bg="gray",
            fg="black",
            font=("Arial", 9),    
            width=20
        )

    def create_serial_devices_refresh_button(self) -> Button:
        button = Button(
            self, 
            text='Refresh', 
            command=self.refresh_serial_devices,
            bg='lightblue',
            activebackground='lightblue'
        )
        return button

    def refresh_serial_devices(self):
        ports = find_available_serial_ports()
        self.serial_devices_combobox.selection_clear()
        self.serial_devices_combobox['values'] = ports 
    
    def create_sensor_serial(self)->SensorSerial:
        port = self.serial_devices_combobox.get()
        baudrate = self.baudrate_combobox.get()

        if port == '' or baudrate == 'Baudrate':
            raise ValueError(f'Incorrect values for: {port=} {baudrate=}')
        
        self.sensor_serial = SensorSerial(
            serial_port=port,
            baudrate=int(baudrate)
        )
    def read_temperature(self)->None:
        if self.sensor_serial is not None:
            temperature = self.sensor_serial.send('TC2')
            if temperature:
                self.temperature_label['text'] = temperature[:-3]
            else:
                self.temperature_label['text'] = 'Error reading temperature'
            return
        raise RuntimeError("Serial connection has not been initialized.")

root = Tk()


if __name__ == '__main__':
    app = App(root)
    root.mainloop()
