import socket
ADDRESS = 'localhost'
PORT = 1111

sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    while True:
        to_send = input("Message to send ->")
        sock.send(to_send.encode('UTF-8'))
except KeyboardInterrupt:
    print ("Exiting App.....")

