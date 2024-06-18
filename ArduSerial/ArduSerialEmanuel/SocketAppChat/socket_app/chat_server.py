import socket
import threading

class ChatServer:
    def __init__(self, host='0.0.0.0', port=3333):
        self.host = host
        self.port = port
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
    
    def start(self):
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"New connection from {client_address}")
                # Manage each client in a separate thread
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.server_socket.close()
    
    def handle_client(self, client_socket, client_address):
        self.clients.append(client_socket)
        try:
            while True:
                message = client_socket.recv(1024)
                if not message:
                    break
                print(f"Received message from {client_address}: {message.decode('utf-8')}")
                # Broadcast the message to all clients
                self.broadcast_message(message, client_socket)
        except Exception as e:
            print(f"Error with client {client_address}: {e}")
        finally:
            print(f"Closing connection with {client_address}")
            self.clients.remove(client_socket)
            client_socket.close()

    def broadcast_message(self, message, sender_socket):
        for client in self.clients:
            if client != sender_socket:  # Avoid sending the message back to the sender
                try:
                    client.sendall(message)
                except Exception as e:
                    print(f"Failed to send message to a client: {e}")

if __name__ == '__main__':
    server = ChatServer(host='0.0.0.0', port=3333)
    server.start()
