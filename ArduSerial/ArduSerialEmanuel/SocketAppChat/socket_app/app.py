from tkinter import Tk

from .ui.chat import ChatContainer
from .ui.connection import SettingsFrame




class App(Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.left_widget = SettingsFrame(self)
        self.right_widget = ChatContainer(self, bg='green')
        
        self.init_gui()
    
    def init_gui(self):
        self.title('SocketApp')
        self.geometry('1000x600')
        self.left_widget.pack(side='left', expand='y')
        self.right_widget.pack(side='right', expand='y')

if __name__ == '__main__':
    app = App()
    app.mainloop()
