import socket               
import threading
from lossy_channel import lossy
from protocol import Frame

class server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((self.host, self.port))
        print("Server started on ", self.host, ":", self.port)

    def send(self, message, client):
        message = message.encode("ascii")
        frame = Frame.create_frame(message)
        lossy_frame = lossy(frame)
        self.s.sendto(lossy_frame, client)
        print("Message sent!")
    
    def receive(self):
        frame, addr = self.s.recvfrom(1024)
        decode_data = Frame.check_frame(frame)
        print("Message received: " + decode_data.decode("ascii"), "from", addr)
    
    def send_thread(self):
        client = ('127.0.0.1', 65432)
        while True:
            message = input("Enter message: ")
            self.send(message, client)
    
    def receive_thread(self):
        while True:
            self.receive()

if __name__ == "__main__":
    s = server('127.0.0.1', 65433)
    
    # Create and start threads
    send_thread = threading.Thread(target=s.send_thread)
    receive_thread = threading.Thread(target=s.receive_thread)
    
    send_thread.start()
    receive_thread.start()
