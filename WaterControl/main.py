import os
import shutil
import uvicorn
import socket
from threading import Thread
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import RPi.GPIO as GPIO

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)

# Inicialización de FastAPI
app = FastAPI()

# Modelo de datos para el comando
class Command(BaseModel):
    mode: str

# Interfaz HTML
@app.get("/", response_class=HTMLResponse)
async def main():
    content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maceta Inteligente</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
                body {
            font-family: Arial, sans-serif;
            background-color: #333;
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            display: flex;
            flex-direction: row;
            width: 1100px;
            height: 580px;
            background-color: #444;
            border-radius: 10px;
            overflow: hidden;
        }
        .sidebar {
            width: 140px;
            background-color: #333;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .content {
            flex-grow: 1;
            padding: 20px;
            display: flex;
            flex-direction: column;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .sidebar .button, .content .button {
            background-color: #555;
            color: #fff;
            border: none;
            padding: 10px 20px;
            margin: 10px 0;
            cursor: pointer;
            border-radius: 5px;
        }
        .sidebar .button:hover, .content .button:hover {
            background-color: #666;
        }
        .input, .select, .checkbox, .radio, .switch {
            margin: 10px 0;
        }
        .tabs {
            display: flex;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .tab {
            background-color: #555;
            color: #fff;
            padding: 10px 20px;
            border-radius: 5px 5px 0 0;
            margin-right: 5px;
        }
        .tab.active {
            background-color: #666;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const socket = io.connect('http://' + document.domain + ':' + location.port);

            function refreshPorts() {
                console.log("Emitting refresh_ports event");
                socket.emit('refresh_ports');
            }

            function changeAppearanceMode(event) {
                const mode = event.target.value;
                console.log(`Emitting change_appearance_mode event with mode: ${mode}`);
                socket.emit('change_appearance_mode', mode);
            }

            function changeScaling(event) {
                const scaling = event.target.value;
                console.log(`Emitting change_scaling event with scaling: ${scaling}`);
                socket.emit('change_scaling', scaling);
            }

            socket.on('ports_list', (ports) => {
                console.log("Received ports_list event with data:", ports);
                const portsSelect = document.getElementById('ports');
                portsSelect.innerHTML = '';
                ports.forEach(port => {
                    const option = document.createElement('option');
                    option.value = port;
                    option.text = port;
                    portsSelect.appendChild(option);
                });
            });

            document.getElementById('refresh-ports-button').addEventListener('click', refreshPorts);
            document.getElementById('appearance-mode').addEventListener('change', changeAppearanceMode);
            document.getElementById('ui-scaling').addEventListener('change', changeScaling);
        });
    </script>
</head>
<body>
    <!-- index.html -->

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maceta Inteligente</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
                body {
            font-family: Arial, sans-serif;
            background-color: #333;
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            display: flex;
            flex-direction: row;
            width: 1100px;
            height: 580px;
            background-color: #444;
            border-radius: 10px;
            overflow: hidden;
        }
        .sidebar {
            width: 140px;
            background-color: #333;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .content {
            flex-grow: 1;
            padding: 20px;
            display: flex;
            flex-direction: column;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .sidebar .button, .content .button {
            background-color: #555;
            color: #fff;
            border: none;
            padding: 10px 20px;
            margin: 10px 0;
            cursor: pointer;
            border-radius: 5px;
        }
        .sidebar .button:hover, .content .button:hover {
            background-color: #666;
        }
        .input, .select, .checkbox, .radio, .switch {
            margin: 10px 0;
        }
        .tabs {
            display: flex;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .tab {
            background-color: #555;
            color: #fff;
            padding: 10px 20px;
            border-radius: 5px 5px 0 0;
            margin-right: 5px;
        }
        .tab.active {
            background-color: #666;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const socket = io.connect('http://' + document.domain + ':' + location.port);

            function refreshPorts() {
                console.log("Emitting refresh_ports event");
                socket.emit('refresh_ports');
            }

            function changeAppearanceMode(event) {
                const mode = event.target.value;
                console.log(`Emitting change_appearance_mode event with mode: ${mode}`);
                socket.emit('change_appearance_mode', mode);
            }

            function changeScaling(event) {
                const scaling = event.target.value;
                console.log(`Emitting change_scaling event with scaling: ${scaling}`);
                socket.emit('change_scaling', scaling);
            }

            socket.on('ports_list', (ports) => {
                console.log("Received ports_list event with data:", ports);
                const portsSelect = document.getElementById('ports');
                portsSelect.innerHTML = '';
                ports.forEach(port => {
                    const option = document.createElement('option');
                    option.value = port;
                    option.text = port;
                    portsSelect.appendChild(option);
                });
            });

            document.getElementById('refresh-ports-button').addEventListener('click', refreshPorts);
            document.getElementById('appearance-mode').addEventListener('change', changeAppearanceMode);
            document.getElementById('ui-scaling').addEventListener('change', changeScaling);
        });
    </script>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2>Maceta Inteligente</h2>
            <select class="select" id="ports"></select>
            <select class="select" id="baudrate">
                <option value="Baudrate">Baudrate</option>
                <option value="9600">9600</option>
                <option value="14400">14400</option>
                <option value="19200">19200</option>
                <option value="38400">38400</option>
                <option value="57600">57600</option>
                <option value="115200">115200</option>
            </select>
            <button id="refresh-ports-button" class="button">Refresh Ports</button>
            <label>Appearance Mode:</label>
            <select class="select" id="appearance-mode">
                <option value="System">System</option>
                <option value="Light">Light</option>
                <option value="Dark">Dark</option>
            </select>
            <label>UI Scaling:</label>
            <select class="select" id="ui-scaling">
                <option value="80%">80%</option>
                <option value="90%">90%</option>
                <option value="100%">100%</option>
                <option value="110%">110%</option>
                <option value="120%">120%</option>
            </select>
            <button class="button" onclick="sendSchedule()">Send Schedule</button>
        </div>
        <div class="content">
             <div class="tabs">
            <div class="tab active" onclick="showTab('tab1')">Set Riego Automático</div>
            <div class="tab" onclick="showTab('tab2')">Duracion de Riego</div>
            <div class="tab" onclick="showTab('tab3')">Regar Cada:</div>
        </div>
        <div id="tab1" class="tab-content active">
            <label>Set Alarm</label>
            <div id="alarm-time">00:00:00</div>
            <label>Hour</label>
            <button class="button" onclick="increaseHour()">+</button>
            <button class="button" onclick="decreaseHour()">-</button>
            <label>Minute</label>
            <button class="button" onclick="increaseMinute()">+</button>
            <button class="button" onclick="decreaseMinute()">-</button>
            <label>Second</label>
            <button class="button" onclick="increaseSecond()">+</button>
            <button class="button" onclick="decreaseSecond()">-</button>
            <button class="button" onclick="sendAlarmTime()">Send Alarm Time</button>
        </div>
        <div id="tab2" class="tab-content">
            <select class="select" id="riego-duration">
                <option value="2">2</option>
                <option value="4">4</option>
                <option value="6">6</option>
                <option value="8">8</option>
                <option value="10">10</option>
            </select>
        </div>
        <div id="tab3" class="tab-content">
            <select class="select" id="regar-cada">
                <option value="6">6</option>
                <option value="8">8</option>
                <option value="10">10</option>
                <option value="12">12</option>
                <option value="14">14</option>
                <option value="16">16</option>
                <option value="18">18</option>
                <option value="20">20</option>
            </select>
        </div>
        </div>
    </div>

    <!-- Incluir el script de Socket.IO -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js" integrity="sha512-Qw9DRlC2w0ME62Nwt2S+I8g5m1Qd3J6Gr2c/T2VlUR3l5P9Zz8sHgWTWLWlHldKwO8L7C3u5GmQxax5FkCEC5A==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
    <script>
        // Configuración de Socket.IO para comunicarse con Flask
        var socket = io();

        // Manejar eventos de Socket.IO (ejemplo)
        socket.on('connect', function() {
            console.log('Conectado al servidor Flask');
        });

        // Aquí puedes agregar más lógica de cliente si es necesario
    </script>
</body>
</html>
	</body>
</html>
    """
    return content

# Endpoint para manejar comandos
@app.post("/command/")
async def send_command(mode: str = Form(...)):
    # Enviar el comando al servidor de sockets de tkinter
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 8001))
        s.sendall(mode.encode())

    if mode == "a":
        print("Modo Automático")
        GPIO.output(6, GPIO.HIGH)
        GPIO.output(4, GPIO.LOW)
        GPIO.output(5, GPIO.LOW)
    elif mode == "m":
        print("Modo Manual")
        GPIO.output(6, GPIO.LOW)
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(5, GPIO.LOW)
    elif mode == "i":
        print("Modo Inteligente")
        GPIO.output(6, GPIO.LOW)
        GPIO.output(4, GPIO.LOW)
        GPIO.output(5, GPIO.HIGH)
    else:
        return {"status": "Invalid mode"}

    return {"status": "Command executed", "mode": mode}

# Evento de cierre para limpiar los GPIO
@app.on_event("shutdown")
async def shutdown_event():
    GPIO.cleanup()
    print("GPIO cleaned up")

# Iniciar aplicación tkinter en un hilo separado
def start_tkinter_app():
    os.system("python app.py")

if __name__ == "__main__":
    tkinter_thread = Thread(target=start_tkinter_app)
    tkinter_thread.start()
    uvicorn.run(app, host="localhost", port=8000)
