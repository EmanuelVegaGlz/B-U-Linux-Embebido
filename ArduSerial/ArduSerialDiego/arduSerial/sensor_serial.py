import time

import serial 

BAUDRATES = [
    2400,
    4800, 
    9600, 
    19200, 
    38400, 
    57600, 
    115200
]
class SensorSerial:

    def __init__(self, 
                serial_port:str,
                baudrate: int=115200, 
                timeout: float = 2.0,
                connection_time: float = 3.0,
                reception_time: float = 0.5 
        ) -> None:
        self.serial_connection = serial.Serial(
            port=serial_port,
            timeout=timeout,
            baudrate=baudrate
        )
        
        self.connection_time = connection_time
        self.reception_time = reception_time
        time.sleep(self.connection_time)
        self.send('hola')
        self.receive()
    
    def send(self, to_send: str)->str|None:
        self.serial_connection.write(to_send.encode('utf-8'))
        time.sleep(self.reception_time)
        received = self.serial_connection.readline()
        return received.decode()
    
    def receive(self, )-> str|None:
        received = self.serial_connection.readline()
        return received
    
    def close(self):
        self.serial_connection.close()
    
    def __del__(self):
        self.close()
    

    def __str__(self) -> str:
        return f"SerialSensor({self.serial_connection}, {self.connection_time=}, {self.reception_time=})"
    def __repr__(self) -> str:
        return f"SerialSensor({self.serial_connection}, {self.connection_time=}, {self.reception_time=})"