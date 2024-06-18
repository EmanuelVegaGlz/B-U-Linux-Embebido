import tkinter as tk
import tkinter.messagebox
import customtkinter as ctk
from tkinter import ttk
from threading import Thread
import RPi.GPIO as GPIO
from datetime import datetime
import time
import socket

from sensor_serial import BAUDRATES, SensorSerial
from utils import find_available_serial_ports

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)

class App(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self.master: ctk.CTk = master
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, rowspan=6, padx=10, pady=10, sticky="nsew")
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Invernadero Inteligente", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        

        # Appearance Mode
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionmenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionmenu.grid(row=9, column=0, padx=20, pady=(10, 10))

        # Scaling
        self.scaling_label = ctk.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.scaling_optionmenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
        self.scaling_optionmenu.grid(row=7, column=0, padx=20, pady=(10, 20))

        # Set initial values
        self.appearance_mode_optionmenu.set("Dark")
        self.scaling_optionmenu.set("100%")

        # GUI objects creations
        self.serial_devices_combobox: ctk.CTkComboBox = self.create_serial_devices_combobox()
        self.refresh_serial_devices_button : ctk.CTkButton = self.create_serial_devices_refresh_button()
        self.baudrate_combobox : ctk.CTkComboBox = self.create_baudrate_combobox()
        self.connect_serial_button: ctk.CTkButton = self.create_connect_serial_button()
        self.temperature_label: ctk.CTkLabel = self.create_temperature_label()
        self.read_temperature_button: ctk.CTkButton = self.create_read_temperature_button()

        # Add GUI objects to sidebar_frame
        self.serial_devices_combobox.grid(row=2, column=0, padx=20, pady=(10, 10))
        self.refresh_serial_devices_button.grid(row=3, column=0, padx=20, pady=(10, 10))
        self.baudrate_combobox.grid(row=4, column=0, padx=20, pady=(10, 10))
        self.connect_serial_button.grid(row=5, column=0, padx=20, pady=(10, 10))
        self.temperature_label.grid(row=0, column=2, padx=20, pady=(10, 10))
        self.read_temperature_button.grid(row=1, column=2, padx=20, pady=(10, 10))

        # Create radiobutton frame
        self.radiobutton_frame = ctk.CTkFrame(self)
        self.radiobutton_frame.grid(row=0, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.radio_var = ctk.IntVar(value=0)
        self.label_radio_group = ctk.CTkLabel(master=self.radiobutton_frame, text="Mode:")
        self.label_radio_group.grid(row=0, column=0, columnspan=1, padx=10, pady=10, sticky="")

        self.radio_button_1 = ctk.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=0, text="Automático", command=self.mode_array)
        self.radio_button_1.grid(row=1, column=0, pady=10, padx=20, sticky="n")

        self.radio_button_2 = ctk.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=1, text="Manual", command=self.mode_array)
        self.radio_button_2.grid(row=2, column=0, pady=10, padx=20, sticky="n")

        self.radio_button_3 = ctk.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=2, text="Inteligente", command=self.mode_array)
        self.radio_button_3.grid(row=3, column=0, pady=10, padx=20, sticky="n")

        # Button to print the array
        self.print_array_button = ctk.CTkButton(self.radiobutton_frame, text="Send Mode", command=self.print_array, width=100)
        self.print_array_button.grid(row=4, column=0, pady=10, padx=20, sticky="n")

        # Labels and components for "Riego Manual" tab
        self.scrollable_frame_regar = ctk.CTkScrollableFrame(self, label_text="Duracion de Riego (minutos)")
        self.scrollable_frame_regar.grid(row=2, column=3, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.scrollable_frame_regar.grid_columnconfigure(0, weight=1)

        self.progressbar_2 = ctk.CTkProgressBar(self.scrollable_frame_regar)
        self.progressbar_2.grid(row=2, column=1, padx=(20, 10), pady=(10, 10), sticky="ew")

        # Center the label by adjusting columnspan and sticky
        self.label_tab_riego2 = ctk.CTkLabel(self.scrollable_frame_regar, text="2            4            6            8            10 ")
        self.label_tab_riego2.grid(row=3, column=1, padx=(20, 10), pady=(10, 10), sticky="ew")

        self.slider_1 = ctk.CTkSlider(self.scrollable_frame_regar, from_=0, to=1, number_of_steps=4)
        self.slider_1.grid(row=4, column=1, padx=(20, 10), pady=(10, 10), sticky="ew")

        # Center the button and align it with the slider and progress bar
        self.string_input_button = ctk.CTkButton(self.scrollable_frame_regar, text="Regar", command=self.return_slider_step)
        self.string_input_button.grid(row=5, column=1, padx=(20, 10), pady=(10, 20), sticky="ew")

        # Link slider and progress bar
        self.slider_1.configure(command=self.progressbar_2.set)

        self.enviar_dato = ctk.CTkButton(self, text="Enviar datos", command=self.create_big_array)
        self.enviar_dato.grid(row=2, column=2, padx=(20, 10), pady=(10, 20), sticky="ew")

        # Other objects
        self.sensor_serial: SensorSerial | None = None
        self.init_gui()

    def init_gui(self) -> None:
        # GUI Config
        self.master.title('Invernadero Inteligente')
        self.master.geometry('1200x800')
        self.pack(fill='both', expand=True)

        # Settings
        self.baudrate_combobox.set('Baudrate')

    def create_serial_devices_combobox(self) -> ctk.CTkComboBox:
        ports = find_available_serial_ports()
        return ctk.CTkComboBox(
            self.sidebar_frame,
            values=ports
        )

    def create_serial_devices_refresh_button(self) -> ctk.CTkButton:
        return ctk.CTkButton(
            self.sidebar_frame,
            text='Refresh devices',
            command=self.refresh_serial_devices,
        )

    def create_baudrate_combobox(self) -> ctk.CTkComboBox:
        return ctk.CTkComboBox(
            self.sidebar_frame,
            values=['Baudrate'] + [str(baudrate) for baudrate in BAUDRATES],
        )

    def create_connect_serial_button(self) -> ctk.CTkButton:
        return ctk.CTkButton(
            self.sidebar_frame,
            text='Connect',
            command=self.create_sensor_serial,
        )

    def create_temperature_label(self) -> ctk.CTkLabel:
        return ctk.CTkLabel(
            self,
            text='XX ºC',
        )

    def create_read_temperature_button(self) -> ctk.CTkButton:
        return ctk.CTkButton(
            self,
            text='Read Temperature',
            command=self.read_temperature,
        )

    def refresh_serial_devices(self):
        ports = find_available_serial_ports()
        self.serial_devices_combobox.set('')
        self.serial_devices_combobox.configure(values=ports)

    def create_sensor_serial(self) -> SensorSerial:
        port = self.serial_devices_combobox.get()
        baudrate = self.baudrate_combobox.get()

        if port == '' or baudrate == 'Baudrate':
            raise ValueError(f'Incorrect values for {port=} {baudrate=}')
        
        self.sensor_serial = SensorSerial(
            serial_port=port,
            baudrate=int(baudrate)
        )

    def read_temperature(self) -> None:
        if self.sensor_serial is not None:
            temperature = self.sensor_serial.send('temp')
            self.temperature_label.configure(text=temperature[:-3])
            return
        raise RuntimeError("Serial connection has not been initialized.")

    def change_appearance_mode_event(self, new_appearance_mode: str) -> None:
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str) -> None:
        scaling_percentage = int(new_scaling.rstrip('%'))
        ctk.set_widget_scaling(scaling_percentage / 100)
    
    def mode_array(self):
        selected_value = self.radio_var.get()
        message = ''
        if selected_value == 0:
            GPIO.output(6, GPIO.HIGH)
            GPIO.output(17, GPIO.LOW)
            GPIO.output(5, GPIO.LOW)
        elif selected_value == 1:
            GPIO.output(6, GPIO.LOW)
            GPIO.output(17, GPIO.HIGH)
            GPIO.output(5, GPIO.LOW)
        elif selected_value == 2:
            GPIO.output(6, GPIO.LOW)
            GPIO.output(17, GPIO.LOW)
            GPIO.output(5, GPIO.HIGH)

        if message:
            self.send_message(message)

        self.radio_array = [1 if i == selected_value else 0 for i in range(3)]

    def print_array(self):
        self.mode_array()  # Ensure radio_array is updated
        str_radio_array = ''.join(str(element) for element in self.radio_array)
        return str_radio_array

    def return_slider_step(self):
        current_step = self.slider_1.get()
        return current_step

    def create_big_array(self):
        big_array = []
        big_array.append(self.print_array())
        big_array.append(self.return_slider_step())
        str_big_array = ''.join(str(element) for element in big_array)
        print(str_big_array)
        if self.sensor_serial is not None:
            self.sensor_serial.send(str_big_array)
        else:
            print("Serial connection not established.")
        return str_big_array

    def close_socket(self):
        self.s.close()
        
    def on_closing(self):
        self.close_socket()
        self.master.destroy()

root = ctk.CTk()

if __name__ == "__main__":
    app = App(root)
    # Uncomment the following line to connect the socket if needed
    # app.s.connect(('0.0.0.0', 4000))
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
