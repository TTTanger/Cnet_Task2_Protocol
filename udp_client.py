import socket
import threading

from lossy_channel import lossy
from protocol import Frame

TIMEOUT = 1.0  # 1s, ACK timeout for retransmission
MAX_RETRY = 10  # Global retry limit

class client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.c.bind((self.host, self.port))
        self.c.settimeout(TIMEOUT)  
        self.seq_num = 0  
        self.expected_seq = 0  
        self.fragment_buffers = {}  # {seq_num: {fragment_id: data}}
        print(f"Client started on {self.host}:{self.port}")

    def send(self, message, server):
        """Send message, automatically choose to fragment or not"""
        if len(message) > Frame.FRAGMENT_SIZE * 2:
            return self.send_fragmented_message(message, server)
        else:
            return self.send_small_message(message, server)
        
    def send_fragmented_message(self, message, server):
        """Send fragmented message"""
        frames = Frame.create_fragmented_frames(self.seq_num, message)
        total_fragments = len(frames)
        
        print(f"Sending fragmented message: {len(message)} bytes, {total_fragments} fragments")
        
        for i, frame in enumerate(frames):
            retries = 0
            
            while retries < MAX_RETRY:
                try:
                    lossy_frame = lossy(frame)
                    self.c.sendto(lossy_frame, server)
                    print(f"Sent fragment {i+1}/{total_fragments} with seq={self.seq_num}")
                    
                    try:
                        ack_frame, addr = self.c.recvfrom(1024)
                        ack_seq, ack_data, _, _ = Frame.check_frame(ack_frame)
                        
                        if ack_data == b'ACK' and ack_seq == self.seq_num:
                            print(f"Received ACK for fragment {i+1}/{total_fragments}")
                            break
                            
                    except socket.timeout:
                        print(f"Timeout for fragment {i+1}, retrying... ({retries + 1})")
                        retries += 1
                        continue
                        
                except Exception as e:
                    print(f"Error sending fragment {i+1}: {e}")
                    retries += 1
            
            if retries >= MAX_RETRY:
                print(f"Failed to send fragment {i+1} after {MAX_RETRY} retries")
                return False
        
        self.seq_num = 1 - self.seq_num
        print(f"All {total_fragments} fragments sent successfully")
        return True
    
    def send_small_message(self, message, server):
        """Send small message"""
        retries = 0

        while retries < MAX_RETRY:
            try:
                frame = Frame.create_frame(self.seq_num, message)
                lossy_frame = lossy(frame)
                self.c.sendto(lossy_frame, server)
                print(f"Sent frame with seq={self.seq_num}")
                try:
                    ack_frame, addr = self.c.recvfrom(1024)
                    ack_seq, ack_data, _, _ = Frame.check_frame(ack_frame)
                    
                    if ack_data == b'ACK' and ack_seq == self.seq_num:
                        print(f"Received ACK for seq={self.seq_num}")
                        self.seq_num = 1 - self.seq_num  
                        return True
                        
                except socket.timeout:
                    print(f"Timeout, retrying... ({retries + 1})")
                    retries += 1
                    continue
                    
            except Exception as e:
                print(f"Error: {e}")
                retries += 1

        print("Max retries reached!")
        return False

    def receive_fragmented_message(self, seq_num, fragment_id, total_fragments, fragment_data, addr):
        """Handle fragmented message"""
        if seq_num not in self.fragment_buffers:
            self.fragment_buffers[seq_num] = {}
        
        self.fragment_buffers[seq_num][fragment_id] = fragment_data
        
        if len(self.fragment_buffers[seq_num]) == total_fragments:
            complete_message = bytearray()
            for i in range(total_fragments):
                if i in self.fragment_buffers[seq_num]:
                    complete_message.extend(self.fragment_buffers[seq_num][i])
                else:
                    print(f"Missing fragment {i} for seq={seq_num}")
                    return
            
            del self.fragment_buffers[seq_num]
            
            complete_data = bytes(complete_message)
            print(f"Reassembled fragmented message: {len(complete_data)} bytes")
            print(f"Complete message: {complete_data.decode('ascii', errors='ignore')[:100]}...")
            
            ack = Frame.create_frame(seq_num, b'ACK')
            self.c.sendto(ack, addr)
            
            if seq_num == self.expected_seq:
                self.expected_seq = 1 - self.expected_seq

    def receive(self):
        try:
            frame, addr = self.c.recvfrom(1024)
            seq_num, decode_data, fragment_id, total_fragments = Frame.check_frame(frame)
            if seq_num is None:
                print(f"Frame check failed: {decode_data}")
                return
                
            print(f"Received message ({len(decode_data)} bytes) from {addr} with seq={seq_num}")
            
            if Frame.is_fragmented(total_fragments):
                print(f"Received fragment {fragment_id + 1}/{total_fragments}")
                self.receive_fragmented_message(seq_num, fragment_id, total_fragments, decode_data, addr)
            else:
                ack = Frame.create_frame(seq_num, b'ACK')
                self.c.sendto(ack, addr)

                if seq_num == self.expected_seq:
                    print(f"Message: {decode_data.decode('ascii')} from {addr}")
                    self.expected_seq = 1 - self.expected_seq
                else:
                    print(f"Duplicate message with seq={seq_num}")

        except socket.timeout:
            pass
        except Exception as e:
            print(f"Error in receive: {e}")

    def send_thread(self):
        server = ('127.0.0.1', 65433)
        while True:
            message = input("Enter message (or 'test_large' for large message test): ").encode('ascii')
            
            if message == b'test_large':
                large_message = b'This is a very large test message that will be fragmented into multiple pieces to handle multiple bit errors more effectively. ' * 20
                print(f"Testing large message: {len(large_message)} bytes")
                self.send(large_message, server)
            else:
                self.send(message, server)
    
    def receive_thread(self):
        while True:
            self.receive()

if __name__ == "__main__":
    c = client('127.0.0.1', 65432)
    
    send_thread = threading.Thread(target=c.send_thread)
    receive_thread = threading.Thread(target=c.receive_thread)
    
    send_thread.start()
    receive_thread.start()