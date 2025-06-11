import socket
import threading
from lossy_channel import lossy
from protocol import Frame

class client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.c.bind((self.host, self.port))
        print("Client started on ", self.host, ":", self.port)

    def send(self, message, server):
        # TODO: Protocol
        frame = Frame.create_frame(message)
        lossy_frame = lossy(frame)
        self.c.sendto(lossy_frame, server)
        print("Message sent!")
    
    def receive(self):
        frame, addr = self.c.recvfrom(1024)
        decode_data = Frame.check_frame(frame)
        print("Message received: " + decode_data.decode("ascii"), "from", addr)

    def send_thread(self):
        server = ('127.0.0.1', 65433)
        while True:
            message = input("Enter message: ").encode('ascii')
            self.send(message, server)
    
    def receive_thread(self):
        while True:
            self.receive()

if __name__ == "__main__":
    c = client('127.0.0.1', 65432)
    
    # Create and start threads
    send_thread = threading.Thread(target=c.send_thread)
    receive_thread = threading.Thread(target=c.receive_thread)
    
    send_thread.start()
    receive_thread.start()
