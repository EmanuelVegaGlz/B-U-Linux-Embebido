import socket
import threading
from tkinter import Button
from tkinter import Canvas
from tkinter import END
from tkinter import Frame
from tkinter import Label
from tkinter import PanedWindow
from tkinter import Scrollbar
from tkinter import Text
from tkinter import Tk
from tkinter import messagebox
from typing import Literal


class ChatCanvas(Canvas):
    def __init__(self, master=None,height=200, *args, **kwargs):
        super().__init__(master=master, height= height, *args, **kwargs)
        self.scrollbar = Scrollbar(master=self, orient="vertical", command=self.yview)
        self.init_gui()
    
    def init_gui(self):
        self.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.pack(side="left", fill="both", expand=True)
    

class TextMessageFrame(Frame):
    def __init__(self, master=None, height=5, *args, **kwargs):
        super().__init__(master=master, height= height, *args, **kwargs)
        self.text_entry = Text(self, height=2)
        self.send_button = Button(self, text="Send", command=self.send_message)
        self.init_gui()
    
    def init_gui(self):
        self.text_entry.pack(side="left", fill="both", padx=10, pady=10, expand=True)
        self.send_button.pack(side="right", padx=10),
    
    def send_message(self):
        message = self.text_entry.get("1.0", END).strip()
        if message:
            # Check if master is ChatContainer and has a method to add a message
            if hasattr(self.master, 'add_message_to_chat'):
                self.master.add_message_to_chat(message, message_type='sent')
            # Clear the text entry box
            self.text_entry.delete("1.0", END)

class MessagesFrame(Frame):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self.canvas = ChatCanvas(master=self, width=400)
        self.messages_frame = Frame(self.canvas,)
        self.canvas.create_window((0, 0), window=self.messages_frame, anchor="nw", height=200, width=600)
        self.messages_frame.bind("<Configure>", self.canvas.configure(scrollregion=self.bbox("all")))
        self.pack(fill="both", expand=True)
    
    def add_message(self, message:str, message_type: Literal['received', 'sent'] = 'sent'):
        anchor = 'ne' if message_type == 'sent' else 'nw'
        justify = 'right' if message_type == 'sent' else 'left'
        bg_color = 'lightgreen' if message_type == 'sent' else 'lightblue'
        Label(self.messages_frame, text=message, wraplength=250, justify=justify, bg=bg_color, foreground='black').pack(anchor=anchor, padx=10, pady=5)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

class ChatContainer(PanedWindow):
    def __init__(self, master=None, orient='vertical', *args, **kwargs):
        super().__init__(master=master, orient=orient, *args, **kwargs)
        self.top_frame = MessagesFrame(self)
        self.bottom_frame = TextMessageFrame(self)
        self.init_gui()

    def init_gui(self):
        self.add(self.top_frame, height=600, stretch="always")  
        self.add(self.bottom_frame, height=200, stretch="always")  
        self.pack(fill="both", expand=True)

    def add_message_to_chat(self, message, message_type: Literal['received', 'sent'] = 'sent'):
        #self.top_frame.add_message(message, message_type=message_type)
        self.top_frame.add_message(message, message_type)
        if message_type == 'sent':
            # Send message through socket if connected
            if self.client_socket:
                try:
                    self.client_socket.sendall(message.encode('utf-8'))
                except Exception as e:
                    messagebox.showerror("Connection Error", str(e))

    def connect_to_server(self, ip, port):
        # Establish socket connection in a separate thread
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, port))
            messagebox.showinfo("Connection", "Connected successfully to the server.")
            # Start a thread to listen for incoming messages
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None

    def receive_messages(self):
        # Thread function to handle incoming messages
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.display_received_message(message)
            except Exception as e:
                messagebox.showerror("Connection Error", str(e))
                break

    def display_received_message(self, message):
        # Method to display received message in the UI
        if self.top_frame.winfo_exists():
            self.top_frame.add_message(message, 'received')

if __name__ == '__main__':
    root = Tk()
    root.geometry('800x800')
    root.title('example')
    chat = ChatContainer(root)
    root.mainloop()
