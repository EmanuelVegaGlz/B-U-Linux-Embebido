import customtkinter as ctk
from sensor_serial import BAUDRATES
from sensor_serial import SensorSerial
from utils import find_available_serial_ports

class App(ctk.CTkFrame):

    def __init__(self, master, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self.master: ctk.CTk = master

        # Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, rowspan=6, padx=10, pady=10, sticky="nsew")

        # Appearance Mode
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=0, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionmenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionmenu.grid(row=1, column=0, padx=20, pady=(10, 10))

        # Scaling
        self.scaling_label = ctk.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=2, column=0, padx=20, pady=(10, 0))
        self.scaling_optionmenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
        self.scaling_optionmenu.grid(row=3, column=0, padx=20, pady=(10, 20))

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
        self.serial_devices_combobox.grid(row=4, column=0, padx=20, pady=(10, 10))
        self.refresh_serial_devices_button.grid(row=5, column=0, padx=20, pady=(10, 10))
        self.baudrate_combobox.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.connect_serial_button.grid(row=7, column=0, padx=20, pady=(10, 10))
        self.temperature_label.grid(row=0, column=1, padx=20, pady=(10, 10))
        self.read_temperature_button.grid(row=1, column=1, padx=20, pady=(10, 10))

        # Other objects
        self.sensor_serial: SensorSerial | None = None
        self.init_gui()

    def init_gui(self) -> None:
        # GUI Config
        self.master.title('example')
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
            text='Refresh available serial devices',
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
            temperature = self.sensor_serial.send('TC2')
            self.temperature_label.configure(text=temperature[:-3])
            return
        raise RuntimeError("Serial connection has not been initialized.")

    def change_appearance_mode_event(self, new_appearance_mode: str) -> None:
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str) -> None:
        scaling_percentage = int(new_scaling.rstrip('%'))
        ctk.set_widget_scaling(scaling_percentage / 100)

root = ctk.CTk()

if __name__ == '__main__':
    app = App(root)
    root.mainloop()
