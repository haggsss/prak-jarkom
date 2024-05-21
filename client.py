import socket
import threading
import sys

def receive(socket, signal):
    while signal[0]:
        try:
            data = socket.recv(1024)  # Increase buffer size for better performance
            if data:
                print(data.decode("utf-8"))
            else:
                raise ConnectionError("No data received")
        except ConnectionError:
            print("You have been disconnected from the server")
            signal[0] = False
        except Exception as e:
            print(f"Error: {e}")
            signal[0] = False

host = input("Host: ")
port = int(input("Port: "))

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
except Exception as e:
    print(f"Could not make a connection to the server: {e}")
    input("Press enter to quit")
    sys.exit(0)

# Use a list to allow the flag to be mutable in the thread
signal = [True]
receiveThread = threading.Thread(target=receive, args=(sock, signal))
receiveThread.start()

try:
    while True:
        message = input()
        if message.lower() == "quit":
            signal[0] = False
            sock.close()
            receiveThread.join()
            break
        sock.sendall(message.encode("utf-8"))
except KeyboardInterrupt:
    print("\nDisconnecting...")
    signal[0] = False
    sock.close()
    receiveThread.join()
except Exception as e:
    print(f"Error: {e}")
finally:
    print("Disconnected from the server")
    sys.exit(0)
