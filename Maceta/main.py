import os
import socket
from threading import Thread
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import RPi.GPIO as GPIO
import uvicorn
import time
import serial

# Configuración de GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)

# Inicialización de FastAPI
app = FastAPI()

# Modelo de datos para el comando
class Command(BaseModel):
    mode: str

# Clase SensorSerial
class SensorSerial:
    def __init__(self, 
                 serial_port: str,
                 baudrate: int = 115200, 
                 timeout: float = 2.0,
                 connection_time: float = 3.0,
                 reception_time: float = 0.5 
        ) -> None:
        try:
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
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            self.serial_connection = None

    def send(self, to_send: str) -> str | None:
        if self.serial_connection:
            self.serial_connection.write(to_send.encode('utf-8'))
            time.sleep(self.reception_time)
            received = self.serial_connection.readline()
            return received.decode()
        return None
    
    def receive(self) -> str | None:
        if self.serial_connection:
            received = self.serial_connection.readline()
            return received.decode()
        return None
    
    def close(self):
        if self.serial_connection:
            self.serial_connection.close()
    
    def __del__(self):
        self.close()

# Inicializar SensorSerial
serial_port = '/dev/ttyACM0'  # Ajustar según sea necesario
sensor = SensorSerial(serial_port=serial_port)

# Función para leer datos del sensor desde Arduino
def read_sensor_data():
    try:
        temperature = sensor.send("GET_TEMP").strip() if sensor else "N/A"
        humidity = sensor.send("GET_HUMIDITY").strip() if sensor else "N/A"
        flow = sensor.send("GET_SOIL_MOISTURE").strip() if sensor else "N/A"

        return temperature, humidity, flow
    except Exception as e:
        print(f"Error reading sensor data: {e}")
        return "N/A", "N/A", "N/A"


# Interfaz HTML
@app.get("/", response_class=HTMLResponse)
async def main():
    temperature, humidity, flow = read_sensor_data()
    
    content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Invernadero Inteligente</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #333; color: #fff; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
            .container {{ width: 500px; background-color: #444; border-radius: 10px; padding: 20px; }}
            .button {{ background-color: #555; color: #fff; border: none; padding: 10px 20px; margin: 10px 0; cursor: pointer; border-radius: 5px; width: 100%; }}
            .button:hover {{ background-color: #666; }}
            .select {{ margin: 10px 0; width: 100%; padding: 10px; }}
        </style>
        <script>
            function sendMode(mode) {{
                fetch('/command/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/x-www-form-urlencoded',
                    }},
                    body: `mode=${{mode}}`
                }})
                .then(response => response.json())
                .then(data => console.log(data));
            }}
        </script>
    </head>
    <body>
        <div class="container">
            <h2>Invernadero Inteligente</h2>
            <p>{temperature}</p>
            <p>{humidity}</p>
            <p>{flow}</p>
            <select class="select" id="mode" onchange="sendMode(this.value)">
                <option value="a">Automático</option>
                <option value="m">Manual</option>
                <option value="i">Inteligente</option>
            </select>
        </div>
    </body>
    </html>
    """
    return content

# Función del servidor de sockets para recibir comandos
def socket_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 4000))
    s.listen(10)
    print("Socket server listening on port 4000")
    
    while True:
        client_socket, addr = s.accept()
        with client_socket:
            print(f"Connected by {addr}")
            mode = client_socket.recv(1024).decode()
            if mode == "a":
                print("Modo Automático")
                GPIO.output(6, GPIO.HIGH)
                GPIO.output(17, GPIO.LOW)
                GPIO.output(5, GPIO.LOW)
            elif mode == "m":
                print("Modo Manual")
                GPIO.output(6, GPIO.LOW)
                GPIO.output(17, GPIO.HIGH)
                GPIO.output(5, GPIO.LOW)
            elif mode == "i":
                print("Modo Inteligente")
                GPIO.output(6, GPIO.LOW)
                GPIO.output(17, GPIO.LOW)
                GPIO.output(5, GPIO.HIGH)
            else:
                print("Invalid mode received")

# Iniciar servidor de sockets en un hilo separado
socket_thread = Thread(target=socket_server)
#socket_thread.daemon = True
#socket_thread.start()

# Endpoint para manejar comandos
@app.post("/command/")
async def send_command(mode: str = Form(...)):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #try:
                #s.connect(('localhost', 8001))
            #except ConnectionRefusedError:
                #return {"status": "Error", "message": "Connection refused to server"}
            
            #s.sendall(mode.encode())
            # Esperar y recibir respuesta si es necesario
            # response = s.recv(1024)
            # print("Respuesta del servidor:", response)
        
            if mode == "a":
                print("Modo Automático")
                GPIO.output(6, GPIO.HIGH)
                GPIO.output(17, GPIO.LOW)
                GPIO.output(5, GPIO.LOW)
            elif mode == "m":
                print("Modo Manual")
                GPIO.output(6, GPIO.LOW)
                GPIO.output(17, GPIO.HIGH)
                GPIO.output(5, GPIO.LOW)
            elif mode == "i":
                print("Modo Inteligente")
                GPIO.output(6, GPIO.LOW)
                GPIO.output(17, GPIO.LOW)
                GPIO.output(5, GPIO.HIGH)
            else:
                return {"status": "Invalid mode"}

        return {"status": "Command executed", "mode": mode}
    except OSError as e:
        print(f"Error handling command: {e}")
        return {"status": "Error", "message": str(e)}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"status": "Error", "message": str(e)}

# Evento de cierre para limpiar los GPIO
@app.on_event("shutdown")
async def shutdown_event():
    GPIO.cleanup()
    print("GPIO cleaned up")
    sensor.close()

# Iniciar aplicación tkinter en un hilo separado
def start_tkinter_app():
    os.system("python app.py")

if __name__ == "__main__":
    tkinter_thread = Thread(target=start_tkinter_app)
    tkinter_thread.start()
    uvicorn.run(app, host='0.0.0.0', port=3000)
