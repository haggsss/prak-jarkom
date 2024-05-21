import socket
import threading

connections = []
total_connections = 0
lock = threading.Lock()

class Client(threading.Thread):
    def __init__(self, socket, address, id, name, signal):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.id = id
        self.name = name
        self.signal = signal
    
    def __str__(self):
        return str(self.id) + " " + str(self.address)
    
    def run(self):
        while self.signal:
            try:
                data = self.socket.recv(1024)  # Increase buffer size for better performance
                if data:
                    print("ID " + str(self.id) + ": " + str(data.decode("utf-8")))
                    self.broadcast(data)
                else:
                    raise ConnectionError("Empty data received")
            except ConnectionError:
                print("Client " + str(self.address) + " has disconnected")
                self.signal = False
                with lock:
                    connections.remove(self)
                break
            except Exception as e:
                print(f"Error: {e}")
                self.signal = False
                with lock:
                    connections.remove(self)
                break
    
    def broadcast(self, data):
        with lock:
            for client in connections:
                if client.id != self.id:
                    try:
                        client.socket.sendall(data)
                    except Exception as e:
                        print(f"Broadcast error to {client.id}: {e}")
                        client.signal = False

def new_connections(socket):
    global total_connections
    while True:
        sock, address = socket.accept()
        with lock:
            total_connections += 1
            client = Client(sock, address, total_connections, "Name", True)
            connections.append(client)
            client.start()
            print("New connection at ID " + str(client))

def main():
    host = input("Host: ")
    port = int(input("Port: "))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)

    new_connections_thread = threading.Thread(target=new_connections, args=(sock,))
    new_connections_thread.start()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Server is shutting down...")
        sock.close()
        for conn in connections:
            conn.signal = False
            conn.socket.close()
        new_connections_thread.join()

if __name__ == "__main__":
    main()
