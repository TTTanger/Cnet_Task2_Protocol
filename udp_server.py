import socket
import threading as t
from lossy_channel import lossy
import protocol

TIMEOUT = 1.0  # 1s, ACK timeout for retransmission
MAX_RETRY = 5

class server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))
        # Set the timeout for receiving ACKs
        self.socket.settimeout(TIMEOUT)
        print(f"Server started on {host}:{port}")

    def send_packet(self, target_socket):
        # Initialize sequence number
        seq_num = 0
        while True:
            # Reset retries for each new packet
            retries = 0
            # Get data to send
            data = input("Enter data to send: ").encode()
            if not data:
                continue
            while retries < MAX_RETRY:
                try:
                    # Create frame
                    frame = protocol.encode(data, seq_num)
                    
                    # Apply lossy channel
                    msg = lossy(frame)
                    
                    # Send the message
                    self.socket.sendto(msg, target_socket)
                    print(f"Sending frame, sequence number: {seq_num}, retries: {retries}")
                    
                    # Wait for ACK
                    try:
                        response, _ = self.socket.recvfrom(1024)
                        if response == b'ACK' + bytes([seq_num]):
                            print("Received ACK")
                            seq_num = (seq_num + 1) % 256  # Sequence number wraps around
                            break

                        else:
                            print("Received incorrect ACK, retransmitting")
                            retries += 1
                    except socket.timeout:
                        print("Timeout waiting for ACK, retransmitting")
                        retries += 1

                except Exception as e:
                    print(f"Error in send_packet: {e}\n")
                    continue
            if retries == MAX_RETRY:
                print("Retransmission limit reached, sending failed")

    def receive_packet(self):
        while True:
            try:
                frame, addr = self.socket.recvfrom(1024)
            except socket.timeout:
                continue # Ignore timeout exceptions and continue waiting for packets
            except Exception as e:
                print(f"Error in receive_packet: {e}")
                continue
            print(f"Received the frame. Length is {len(frame)} bytes from {addr}")

            # Decode the frame
            data, seq_num, has_error = protocol.decode(frame)

            if has_error:
                print("Failed to decode the frame, error detected.")
                continue

            print(f"Successfully decoded the frame. Sequence number is: {seq_num}")
            print(f"Original data: {data.decode(errors='replace')}")

            # Send ACK
            self.socket.sendto(b'ACK' + bytes([seq_num]), addr)
            print("ACK sent")

if __name__ == "__main__":
    server_object = server("127.0.0.1", 65433)
    client_addr = ("127.0.0.1", 65432)
    t1 = t.Thread(target=server_object.send_packet, args=(client_addr,))
    t2 = t.Thread(target=server_object.receive_packet)
    t1.start()
    t2.start()