import tkinter as tk
import tkinter.messagebox
import customtkinter
import customtkinter as ctk
from threading import Thread
from datetime import datetime
import time
import socket
import RPi.GPIO as GPIO

from sensor_serial import BAUDRATES
from sensor_serial import SensorSerial
from utils import find_available_serial_ports

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

s = socket.socket()
s.bind(('localhost', 8001))
s.listen(5)

class App(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configuración de la ventana
        self.title("Maceta Inteligente")
        self.geometry(f"{1100}x{580}")

        # Configuración del layout de la ventana
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Creación de sidebar con widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Maceta Inteligente", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Otras configuraciones y widgets omitidos por brevedad...

        # Inicializar el hilo de verificación de alarma
        self.alarm_thread = Thread(target=self.check_alarm)
        self.alarm_thread.daemon = True
        self.alarm_thread.start()

        # Hilo para manejar la conexión de socket
        self.socket_thread = Thread(target=self.handle_socket_connection)
        self.socket_thread.daemon = True
        self.socket_thread.start()

        # Adjustments
        self.optionmenu_1 = customtkinter.CTkOptionMenu(self.sidebar_frame, dynamic_resizing=False, values=find_available_serial_ports())
        self.optionmenu_1.grid(row=1, column=0, padx=20, pady=10)      
        self.combobox_1 = customtkinter.CTkComboBox(self.sidebar_frame, values=['Baudrate'] + [str(rate) for rate in BAUDRATES])
        self.combobox_1.grid(row=2, column=0, padx=20, pady=10)
        self.string_input_button = customtkinter.CTkButton(self.sidebar_frame, text="Refresh Ports", command=self.create_sensor_serial)
        self.string_input_button.grid(row=3, column=0, padx=20, pady=(10, 10))

        #Apperance
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # create main entry and button
        self.entry = customtkinter.CTkEntry(self, placeholder_text="CTkEntry")
        self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.main_button_1 = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=250)
        self.tabview.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add(" Set Riego Automático")
        self.tabview.add("Duracion de Riego")
        self.tabview.add("Regar Cada:")
        self.tabview.tab(" Set Riego Automático").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Duracion de Riego").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Regar Cada:").grid_columnconfigure(0, weight=1)


        
        #Duracion de Riego 
        self.combobox_riego = customtkinter.CTkComboBox(self.tabview.tab("Duracion de Riego"), values=["2","4","6", "8", "10"])
        self.combobox_riego.grid(row=0, column=0, padx=20, pady=(10, 10))
        self.string_input_button = customtkinter.CTkButton(self.tabview.tab("Duracion de Riego"), text="Set Riego",command=self.create_sensor_serial)
        self.string_input_button.grid(row=2, column=0, padx=20, pady=(10, 10))
    
        # Regar Cada tab with checkboxes
        self.checkbox_array = []

        self.checkbox_1 = customtkinter.CTkCheckBox(self.tabview.tab("Regar Cada:"), text="24 horas", command=lambda: self.checkbox_selected(1))
        self.checkbox_1.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="n")
        self.checkbox_2 = customtkinter.CTkCheckBox(self.tabview.tab("Regar Cada:"), text="12 horas", command=lambda: self.checkbox_selected(2))
        self.checkbox_2.grid(row=2, column=0, pady=(20, 0), padx=20, sticky="n")

        # Button to print the array
        self.print_button = customtkinter.CTkButton(self.tabview.tab("Regar Cada:"), text="Print Array", command=self.print_checkbox_array)
        self.print_button.grid(row=3, column=0, pady=(20, 0), padx=20, sticky="n")

        
        # Set Riego - Alarm Clock Settings
        self.alarm_hour = 0
        self.alarm_minute = 0
        self.alarm_second = 0
        self.alarm_set = False

        self.label_tab_2 = ctk.CTkLabel(self.tabview.tab(" Set Riego Automático"), text="Set Alarm")
        self.label_tab_2.grid(row=0, column=2, padx=20, pady=(20, 10))

        self.alarm_time_label = ctk.CTkLabel(self.tabview.tab(" Set Riego Automático"), text="00:00:00")
        self.alarm_time_label.grid(row=2, column=1, padx=10, pady=5)

        self.label_tab_3 = ctk.CTkLabel(self.tabview.tab(" Set Riego Automático"), text="Hour")
        self.label_tab_3.grid(row=2, column=2, padx=5, pady=5 )
        self.increase_hour_button = ctk.CTkButton(self.tabview.tab(" Set Riego Automático"), text=" +", command=self.increase_hour, width=50)
        self.increase_hour_button.grid(row=3, column=2, padx=5, pady=5 )
        self.decrease_hour_button = ctk.CTkButton(self.tabview.tab(" Set Riego Automático"), text=" -", command=self.decrease_hour, width=50)
        self.decrease_hour_button.grid(row=4, column=2, padx=5, pady=5 )

        self.label_tab_4 = ctk.CTkLabel(self.tabview.tab(" Set Riego Automático"), text="Minute")
        self.label_tab_4.grid(row=2, column=3, padx=10, pady=5 )
        self.increase_minute_button = ctk.CTkButton(self.tabview.tab(" Set Riego Automático"), text=" +", command=self.increase_minute, width=50)
        self.increase_minute_button.grid(row=3, column=3, padx=10, pady=5 )
        self.decrease_minute_button = ctk.CTkButton(self.tabview.tab(" Set Riego Automático"), text=" -", command=self.decrease_minute, width=50)
        self.decrease_minute_button.grid(row=4, column=3, padx=10, pady=5 )

        self.label_tab_5 = ctk.CTkLabel(self.tabview.tab(" Set Riego Automático"), text="Second")
        self.label_tab_5.grid(row=2, column=4, padx=10, pady=5 )
        self.increase_second_button = ctk.CTkButton(self.tabview.tab(" Set Riego Automático"), text=" +", command=self.increase_second, width=50)
        self.increase_second_button.grid(row=3, column=4,padx=20, pady=5 )
        self.decrease_second_button = ctk.CTkButton(self.tabview.tab(" Set Riego Automático"), text=" -", command=self.decrease_second, width=50)
        self.decrease_second_button.grid(row=4, column=4, padx=10, pady=5 )

        # Button to send alarm time string
        self.send_alarm_button = ctk.CTkButton(self.tabview.tab(" Set Riego Automático"), text="Send Alarm Time", command=self.send_alarm_time, width=150)
        self.send_alarm_button.grid(row=5, column=2, padx=10, pady=5)


        # Set default values
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        self.combobox_1.set("Baudrate")
        self.optionmenu_1.set("Ports")

        # Start the alarm check thread
        self.alarm_thread = Thread(target=self.check_alarm)
        self.alarm_thread.daemon = True
        self.alarm_thread.start()


        # Create radiobutton frame
        self.radiobutton_frame = ctk.CTkFrame(self)
        self.radiobutton_frame.grid(row=1, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")
        
        self.radio_var = tk.IntVar(value=0)
        self.label_radio_group = ctk.CTkLabel(master=self.radiobutton_frame, text="Mode:")
        self.label_radio_group.grid(row=0, column=2, columnspan=1, padx=10, pady=10, sticky="")
        
        self.radio_button_1 = ctk.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=0, text="Automatico", command=self.mode_array)
        self.radio_button_1.grid(row=1, column=2, pady=10, padx=20, sticky="n")
        
        self.radio_button_2 = ctk.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=1, text="Manual", command=self.mode_array)
        self.radio_button_2.grid(row=2, column=2, pady=10, padx=20, sticky="n")
        
        self.radio_button_3 = ctk.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=2, text="Inteligente", command=self.mode_array)
        self.radio_button_3.grid(row=3, column=2, pady=10, padx=20, sticky="n")

        # Button to print the array
        self.print_array_button = ctk.CTkButton(self.radiobutton_frame, text="Send Mode", command=self.print_array, width=100)
        self.print_array_button.grid(row=4, column=2, pady=10, padx=20, sticky="n")

        # Initialize the array
        self.radio_array = [0, 0, 0]


# create tabview
        self.tabview = customtkinter.CTkTabview(self, width=250)
        self.tabview.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("Nivel de Humedad")
        self.tabview.add("Riego Manual")

        # create slider and progressbar frame
        self.slider_progressbar_frame = customtkinter.CTkFrame(self.tabview.tab("Riego Manual"), fg_color="transparent")
        self.slider_progressbar_frame.grid(row=0, column=0,  sticky="nsew")
        self.slider_progressbar_frame.grid_columnconfigure(0, weight=1)
        self.slider_progressbar_frame.grid_rowconfigure(0, weight=1)

        self.progressbar_2 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_2.grid(row=1, column=2, padx=(20, 10), pady=(10, 10), sticky="ew")

        self.slider_1 = customtkinter.CTkSlider(self.slider_progressbar_frame, from_=0, to=1, number_of_steps=5)
        self.slider_1.grid(row=2, column=2, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.string_input_button = customtkinter.CTkButton(self.tabview.tab("Riego Manual"), text="Regar",command=self.create_sensor_serial)
        self.string_input_button.grid(row=3, column=2, padx=20, pady=(10, 10))


 # Create scrollable frame
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text="Selecciona día de Riego")
        self.scrollable_frame.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        self.switch_vars = []
        self.scrollable_frame_switches = []
        self.days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

        
        for index, day in enumerate(self.days):
            switch_var = customtkinter.StringVar(value="off")
            switch = customtkinter.CTkSwitch(
                master=self.scrollable_frame, 
                text=day, 
                variable=switch_var, 
                onvalue="on", 
                offvalue="off"
            )
            switch.grid(row=index+2, column=0, padx=10, pady=(0, 20))
            self.switch_vars.append(switch_var)
            self.scrollable_frame_switches.append(switch)
            
         # Button to print the schedule array
        self. get_schedule_button= customtkinter.CTkButton(self.sidebar_frame, text="Send Schedule", command=self.get_schedule)
        self.get_schedule_button .grid(row=4, column=0, padx=20, pady=(10, 10))        


        # set default values
        self.checkbox_1.select()
        self.scrollable_frame_switches[0].select()
        self.scrollable_frame_switches[4].select()

        
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        self.combobox_1.set("Baudrate") 
        self.optionmenu_1.set("Ports")
        self.combobox_riego.set("Minutos")
        
        
        self.slider_1.configure(command=self.progressbar_2.set)

        #self.textbox.insert("0.0", "CTkTextbox\n\n" + "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\n" * 20))
  
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)
    def sidebar_button_event(self):
        print("sidebar_button click")
    def refresh_serial_devices(self):
        ports = find_available_serial_ports()
        self.serial_devices_combobox.selection_clear()
        self.serial_devices_combobox['values'] = ports
    def create_sensor_serial(self)->SensorSerial:
        port = self.serial_devices_combobox.get()
        baudrate = self.baudrate_combobox.get()

        if port == '' or baudrate == 'Baudrate':
            raise ValueError(f'Incorrect values for {port=} {baudrate=}')
        
        self.sensor_serial = SensorSerial(
            serial_port=port,
            baudrate=int(baudrate)
        )       
    def get_schedule(self):
        schedule = [1 if var.get() == "on" else 0 for var in self.switch_vars]
        print("Schedule Array:", schedule)
    def select_day(self, day_index):
        if 0 <= day_index < len(self.scrollable_frame_switches):
            self.scrollable_frame_switches[day_index].select()       
    def increase_hour(self):
        self.alarm_hour = (self.alarm_hour + 1) % 24
        self.update_alarm_time_label()
    def decrease_hour(self):
        self.alarm_hour = (self.alarm_hour - 1) % 24
        self.update_alarm_time_label()
    def increase_minute(self):
        self.alarm_minute = (self.alarm_minute + 5) % 60
        self.update_alarm_time_label()
    def decrease_minute(self):
        self.alarm_minute = (self.alarm_minute - 5) % 60
        self.update_alarm_time_label()
    def increase_second(self):
        self.alarm_second = (self.alarm_second + 15) % 60
        self.update_alarm_time_label()
    def decrease_second(self):
        self.alarm_second = (self.alarm_second - 15) % 60
        self.update_alarm_time_label()
    def update_alarm_time_label(self):
        self.alarm_time_label.configure(text=f"{self.alarm_hour:02}:{self.alarm_minute:02}:{self.alarm_second:02}")      
    def set_alarm(self):
        self.alarm_set = True
        alarm_time_str = self.get_alarm_time_str()
        print(f"Alarm set for: {alarm_time_str}")
        # Here you can add any functionality to handle the alarm time string
    def get_alarm_time_str(self):
        return f"{self.alarm_hour:02}:{self.alarm_minute:02}:{self.alarm_second:02}"
    def send_alarm_time(self):
        alarm_time_str = self.get_alarm_time_str()
        # Functionality to send the alarm time string
        print(f"Sending alarm time: {alarm_time_str}")
        # Here you can add the logic to send this string to another component or system
    def check_alarm(self):
        while True:
            if self.alarm_set:
                now = datetime.now()
                if (now.hour == self.alarm_hour and
                        now.minute == self.alarm_minute and
                        now.second == self.alarm_second):
                    self.alarm_set = False
                    tkinter.messagebox.showinfo("Alarm", "Regando!")
            time.sleep(1)
    def mode_array(self):
        selected_value = self.radio_var.get()
        if selected_value == 0:
           s.send("a".encode())
        elif selected_value == 1:
            s.send("m".encode())
        elif selected_value == 2:
            s.send("i".encode())
        self.radio_array = [1 if i == selected_value else 0 for i in range(3)]
        
    def print_array(self):
        print(self.radio_array)
        
    def checkbox_selected(self, checkbox_id):
        self.checkbox_array.append(checkbox_id)
        print(checkbox_id)

        
    def print_checkbox_array(self):
        print(self.checkbox_array)


    def handle_socket_connection(self):
        s.bind(('localhost', 8001))
        s.listen(5)
        while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    mode = data.decode()
                    print("Received mode:", mode)
                    self.update_mode(mode)

    def update_mode(self, mode):
        # Update UI and send GPIO commands based on the received mode
        if mode == 'a':
            print("Modo Automático recibido")
            self.radio_var.set(0)
            self.radio_button_1.select()
            GPIO.output(6, GPIO.HIGH)
            GPIO.output(4, GPIO.LOW)
            GPIO.output(5, GPIO.LOW)
        elif mode == 'm':
            print("Modo Manual recibido")
            self.radio_var.set(1)
            self.radio_button_2.select()
            GPIO.output(6, GPIO.LOW)
            GPIO.output(4, GPIO.HIGH)
            GPIO.output(5, GPIO.LOW)
        elif mode == 'i':
            print("Modo Inteligente recibido")
            self.radio_var.set(2)
            self.radio_button_3.select()
            GPIO.output(6, GPIO.LOW)
            GPIO.output(4, GPIO.LOW)
            GPIO.output(5, GPIO.HIGH)
        else:
            print("Modo no válido recibido:", mode)

    

if __name__ == "__main__":
    app = App()
    app.mainloop()
