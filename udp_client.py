import socket
import threading
from lossy_channel import lossy

class client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.c.bind((self.host, self.port))
        print("Client started on ", self.host, ":", self.port)

    def send(self, message, server):
        broken_message = lossy(message)
        self.c.sendto(broken_message, server)
        print("Message sent: " + broken_message.decode())
    
    def receive(self):
        # TODO: Protocol
        # raw_message = self.c.recvfrom(1024)
        # Check logistic: If message is valid, fix it. If not, resend it
        data, addr = self.c.recvfrom(1024)
        print("Message received: " + data.decode(), "from", addr)

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
