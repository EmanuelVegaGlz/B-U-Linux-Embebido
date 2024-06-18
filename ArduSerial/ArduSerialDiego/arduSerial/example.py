import time
import serial
PORT = '/dev/ttyACM0'
BAUDRATE = 115200

arduino = serial.Serial(
    port=PORT,
    baudrate=BAUDRATE,
    timeout=2
)

arduino.write(b'hola')
time.sleep(.5)
received = arduino.readline()
print(received)

for i in range(1, 4):
    to_send = f"Prueba {i}"
    arduino.write(to_send.encode(encoding="utf-8"))
    print(f"Envidado: {to_send}")
    time.sleep(.5)
    received = arduino.readline()
    print(f"Recibido: {received}")
    
arduino.close()