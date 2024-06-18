from tkinter import Frame, Entry, Button, Label, messagebox
import socket
import threading

class SettingsFrame(Frame):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self['bg'] = 'white'
        
        
        self.ip_address_label = Label(self, text="IP Address:", bg='black', foreground='lightgreen')
        self.ip_address_entry = Entry(self, width=20)
        self.ip_address_hint = "e.g. 192.168.1.1"
        self.ip_address_entry.insert(0, self.ip_address_hint)
        
        self.port_label = Label(self, text="Port:", bg='black', foreground='lightgreen')
        self.port_entry = Entry(self, width=10)
        self.port_hint = "e.g. 8080"
        self.port_entry.insert(0, self.port_hint)
        
        self.connect_button = Button(self, text="Connect", command=self.connect_to_server)
        
        self.init_gui()
        self.bind_entry_events()

    def init_gui(self):
        
        self.ip_address_label.pack(side='top', padx=5, pady=5, expand=True, fill='x')
        self.ip_address_entry.pack(side='top', padx=5, pady=5)
        self.port_label.pack(side='top', padx=5, pady=5, expand=True, fill='x')
        self.port_entry.pack(side='top', padx=5, pady=5)
        self.connect_button.pack(side='top', padx=5, pady=5, expand=True, fill='x')

    def bind_entry_events(self):
        # Bind focus-in and focus-out events for IP Address entry
        self.ip_address_entry.bind("<FocusIn>", self.clear_hint)
        self.ip_address_entry.bind("<FocusOut>", self.restore_hint)
        
        # Bind focus-in and focus-out events for Port entry
        self.port_entry.bind("<FocusIn>", self.clear_hint)
        self.port_entry.bind("<FocusOut>", self.restore_hint)

    def clear_hint(self, event):
        # Clear the hint text when the user focuses on the widget
        if event.widget == self.ip_address_entry and self.ip_address_entry.get() == self.ip_address_hint:
            self.ip_address_entry.delete(0, "end")
        elif event.widget == self.port_entry and self.port_entry.get() == self.port_hint:
            self.port_entry.delete(0, "end")

    def restore_hint(self, event):
        # Restore the hint text if the user leaves the widget empty
        if event.widget == self.ip_address_entry and not self.ip_address_entry.get():
            self.ip_address_entry.insert(0, self.ip_address_hint)
        elif event.widget == self.port_entry and not self.port_entry.get():
            self.port_entry.insert(0, self.port_hint)

    def connect_to_server(self):
        # Get the current values of IP and Port, excluding hints
        ip_address = self.ip_address_entry.get()
        port = self.port_entry.get()
        if ip_address == self.ip_address_hint or not ip_address:
            messagebox.showerror("Connection Error", "Please enter a valid IP Address")
            return
        if port == self.port_hint or not port.isdigit():
            messagebox.showerror("Connection Error", "Please enter a valid Port")
            return
        try:
            port = int(port)
            # Starting a new thread to manage the socket connection
            threading.Thread(target=self.master.right_widget.connect_to_server, args=(ip_address, port), daemon=True).start()
        except ValueError:
            messagebox.showerror("Connection Error", "Invalid port number. Please enter a number.")
# Example usage
if __name__ == '__main__':
    from tkinter import Tk
    root = Tk()
    root.geometry('400x100')
    settings_frame = SettingsFrame(root)
    settings_frame.pack(fill='both', expand=True)
    root.mainloop()
