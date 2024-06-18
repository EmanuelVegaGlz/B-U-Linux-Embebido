#example_server

import socket 
import time 

ADDRESS = "localhost"
PORT = 1111

sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind((ADDRESS,PORT))
sock.listen()

connection, address,  = sock.accept()
print(f"accepted connectionn from: {address}")

try:
    while True:
        received = connection.rec(1024)
        print("RECEIVED:", received.decode())
        time.sleep(0.5)
except KeyboardInterrupt:
    print("exiting app...")
except Exception as e:
    print(f"something went wrong {e}")
finally:
    connection.close()
    sock.close()