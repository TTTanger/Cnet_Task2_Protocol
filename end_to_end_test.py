import os
import time
import statistics
from protocol import Frame
from udp_client import client as Client
from udp_server import server as Server
import threading
import datetime

LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, f'end_to_end_test_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

os.makedirs(LOG_DIR, exist_ok=True)

DATA_SIZES = [16, 32, 64, 128, 256, 512, 1024, 2048]
ITERATIONS = 5
CLIENT_ADDR = ('127.0.0.1', 65432)
SERVER_ADDR = ('127.0.0.1', 65433)

class TestResult:
    def __init__(self):
        self.success = 0
        self.total = 0
        self.latencies = []
        self.fragments = []
        self.bytes_sent = 0

    def record(self, success, latency, fragments, size):
        self.total += 1
        if success:
            self.success += 1
            self.latencies.append(latency)
        self.fragments.append(fragments)
        self.bytes_sent += size

    def summary(self):
        success_rate = self.success / self.total * 100 if self.total else 0
        avg_latency = statistics.mean(self.latencies) * 1000 if self.latencies else 0
        avg_fragments = statistics.mean(self.fragments) if self.fragments else 0
        return success_rate, avg_latency, avg_fragments, self.bytes_sent

def run_direction_test(sender, receiver_addr, direction_label):
    results = {}
    for size in DATA_SIZES:
        res = TestResult()
        for _ in range(ITERATIONS):
            message = os.urandom(size)
            # Count fragments
            if size > Frame.FRAGMENT_SIZE * 2:
                fragments = len(Frame.create_fragmented_frames(sender.seq_num, message))
            else:
                fragments = 1
            start = time.time()
            success = sender.send(message, receiver_addr)
            end = time.time()
            latency = end - start
            res.record(success, latency, fragments, size)
            time.sleep(0.001)
        results[size] = res
    return results

def write_log(results_c2s, results_s2c):
    with open(LOG_FILE, 'w') as f:
        f.write('--- End-to-End Test Report ---\n')
        f.write('Each entry: Data size | Avg fragments | Success rate | Avg latency (ms) | Bandwidth (KB/s)\n\n')
        f.write('[Direction] Client -> Server\n')
        for size in DATA_SIZES:
            res = results_c2s[size]
            success_rate, avg_latency, avg_fragments, bytes_sent = res.summary()
            duration = (avg_latency/1000) * res.success if res.success else 1
            bandwidth = (bytes_sent/1024) / duration if duration > 0 else 0
            f.write(f'Data size: {size:5d} | Fragments: {avg_fragments:.2f} | Success: {success_rate:6.2f}% | Avg latency: {avg_latency:8.2f} ms | Bandwidth: {bandwidth:8.2f} KB/s\n')
        f.write('\n[Direction] Server -> Client\n')
        for size in DATA_SIZES:
            res = results_s2c[size]
            success_rate, avg_latency, avg_fragments, bytes_sent = res.summary()
            duration = (avg_latency/1000) * res.success if res.success else 1
            bandwidth = (bytes_sent/1024) / duration if duration > 0 else 0
            f.write(f'Data size: {size:5d} | Fragments: {avg_fragments:.2f} | Success: {success_rate:6.2f}% | Avg latency: {avg_latency:8.2f} ms | Bandwidth: {bandwidth:8.2f} KB/s\n')
        f.write('\n--- End of Report ---\n')

def main():
    # Start client and server instances
    c = Client(*CLIENT_ADDR)
    s = Server(*SERVER_ADDR)
    threading.Thread(target=c.receive_thread, daemon=True).start()
    threading.Thread(target=s.receive_thread, daemon=True).start()
    time.sleep(1)
    # Client → Server
    results_c2s = run_direction_test(c, SERVER_ADDR, 'Client -> Server')
    # Server → Client
    results_s2c = run_direction_test(s, CLIENT_ADDR, 'Server -> Client')
    # Write log
    write_log(results_c2s, results_s2c)
    print(f'End-to-end test completed. See {LOG_FILE}')

if __name__ == '__main__':
    main() 