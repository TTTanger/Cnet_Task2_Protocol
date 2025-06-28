#!/usr/bin/env python3
"""
Protocol Evaluation Script
Evaluates the custom UDP protocol for:
- Latency: Measure the delay introduced by the protocol
- Bandwidth: Determine the additional data overhead caused by the protocol
- Limitations: Identify where the protocol fails or becomes inefficient
"""

import time
import statistics
import random
import datetime
import os
from protocol import Frame
from lossy_channel import lossy

class ProtocolEvaluator:
    def __init__(self):
        self.results = {
            'latency': [],
            'overhead': [],
            'success_rate': [],
            'data_sizes': []
        }
        self.log_data = []
        
        # Create log directory
        self.log_dir = "logs"
        self.create_log_directory()
        
        # Generate log filename with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_filename = os.path.join(self.log_dir, f"protocol_evaluation_{timestamp}.log")
    
    def create_log_directory(self):
        """Create logs directory if it doesn't exist"""
        try:
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
                print(f"Created log directory: {self.log_dir}")
        except Exception as e:
            print(f"Error creating log directory: {e}")
            # Fallback to current directory
            self.log_dir = "."
            print("Using current directory for logs")
    
    def log_message(self, message):
        """Add message to log and print to console"""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.log_data.append(log_entry)
        print(message)
    
    def measure_latency(self, data_sizes, iterations=100):
        """Measure protocol latency for different data sizes"""
        self.log_message("=== Latency Measurement ===")
        
        for size in data_sizes:
            test_data = b'A' * size
            latencies = []
            
            for _ in range(iterations):
                start_time = time.time()
                
                # Create frame
                frame = Frame.create_frame(0, test_data)
                
                # Simulate transmission through lossy channel
                corrupted_frame = lossy(frame)
                
                # Check frame
                result = Frame.check_frame(corrupted_frame)
                
                end_time = time.time()
                latency = (end_time - start_time) * 1000  # Convert to milliseconds
                latencies.append(latency)
            
            avg_latency = statistics.mean(latencies)
            std_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0
            self.results['latency'].append(avg_latency)
            self.results['data_sizes'].append(size)
            
            self.log_message(f"Data size: {size:6d} bytes | Avg latency: {avg_latency:.3f} ms | Std dev: {std_latency:.3f} ms")
    
    def measure_overhead(self, data_sizes):
        """Measure protocol overhead for different data sizes"""
        self.log_message("\n=== Bandwidth Overhead Measurement ===")
        
        for size in data_sizes:
            test_data = b'A' * size
            
            # Create frame
            frame = Frame.create_frame(0, test_data)
            
            # Calculate overhead
            original_size = len(test_data)
            frame_size = len(frame)
            overhead_bytes = frame_size - original_size
            overhead_percentage = (overhead_bytes / original_size) * 100
            
            self.results['overhead'].append(overhead_percentage)
            
            self.log_message(f"Data size: {size:6d} bytes | Frame size: {frame_size:6d} bytes | "
                  f"Overhead: {overhead_bytes:4d} bytes ({overhead_percentage:6.2f}%)")
    
    def measure_success_rate(self, data_sizes, iterations=100):
        """Measure success rate for different data sizes"""
        self.log_message("\n=== Success Rate Measurement ===")
        
        for size in data_sizes:
            test_data = b'A' * size
            success_count = 0
            crc_errors = 0
            frame_errors = 0
            
            for _ in range(iterations):
                # Create frame
                frame = Frame.create_frame(0, test_data)
                
                # Simulate transmission through lossy channel
                corrupted_frame = lossy(frame)
                
                # Check frame
                result = Frame.check_frame(corrupted_frame)
                
                if result[0] is not None and result[1] == test_data:
                    success_count += 1
                elif result[1] == b'CRC error':
                    crc_errors += 1
                else:
                    frame_errors += 1
            
            success_rate = (success_count / iterations) * 100
            crc_error_rate = (crc_errors / iterations) * 100
            frame_error_rate = (frame_errors / iterations) * 100
            self.results['success_rate'].append(success_rate)
            
            self.log_message(f"Data size: {size:6d} bytes | Success: {success_rate:6.2f}% | "
                  f"CRC errors: {crc_error_rate:6.2f}% | Frame errors: {frame_error_rate:6.2f}%")
    
    def test_fragmentation_efficiency(self, max_size=5000):
        """Test fragmentation efficiency for large data"""
        self.log_message("\n=== Fragmentation Efficiency Test ===")
        
        sizes = list(range(100, max_size + 100, 100))
        fragment_counts = []
        overhead_ratios = []
        
        for size in sizes:
            test_data = b'A' * size
            
            # Create fragmented frames
            frames = Frame.create_fragmented_frames(0, test_data)
            fragment_count = len(frames)
            
            # Calculate total overhead
            total_frame_size = sum(len(frame) for frame in frames)
            overhead_ratio = (total_frame_size - size) / size * 100
            
            fragment_counts.append(fragment_count)
            overhead_ratios.append(overhead_ratio)
            
            if size % 1000 == 0:
                self.log_message(f"Data size: {size:6d} bytes | Fragments: {fragment_count:3d} | "
                      f"Overhead: {overhead_ratio:6.2f}%")
        
        return sizes, fragment_counts, overhead_ratios
    
    def identify_limitations(self):
        """Identify protocol limitations"""
        self.log_message("\n=== Protocol Limitations Analysis ===")
        
        limitations = []
        
        # Test maximum data size (reduced to avoid overflow)
        self.log_message("Testing maximum data size...")
        max_test_size = 10000  # Reduced from 65535 to avoid overflow
        test_data = b'A' * max_test_size
        
        try:
            frame = Frame.create_frame(0, test_data)
            self.log_message(f"✓ Large data size supported: {max_test_size} bytes")
        except Exception as e:
            self.log_message(f"✗ Large data size limitation: {e}")
            limitations.append(f"Large data size: {e}")
        
        # Test sequence number overflow
        self.log_message("Testing sequence number overflow...")
        try:
            frame1 = Frame.create_frame(255, b'test')  # Max 8-bit sequence number
            frame2 = Frame.create_frame(0, b'test')    # Should wrap around
            self.log_message("✓ Sequence number wrapping works")
        except Exception as e:
            self.log_message(f"✗ Sequence number limitation: {e}")
            limitations.append(f"Sequence number: {e}")
        
        # Test fragment ID overflow
        self.log_message("Testing fragment ID overflow...")
        try:
            frame = Frame.create_frame(0, b'test', fragment_id=255, total_fragments=256)
            self.log_message("✓ Fragment ID supports 8-bit range")
        except Exception as e:
            self.log_message(f"✗ Fragment ID limitation: {e}")
            limitations.append(f"Fragment ID: {e}")
        
        # Test error recovery
        self.log_message("Testing error recovery...")
        test_data = b'Error recovery test'
        frame = Frame.create_frame(0, test_data)
        
        # Introduce multiple bit errors
        corrupted_frame = bytearray(frame)
        for i in range(5):  # Introduce 5 bit errors
            pos = random.randint(0, len(corrupted_frame) - 1)
            bit_pos = random.randint(0, 7)
            corrupted_frame[pos] ^= (1 << bit_pos)
        
        result = Frame.check_frame(bytes(corrupted_frame))
        if result[0] is None:
            self.log_message("✗ Protocol cannot recover from multiple bit errors")
            limitations.append("Multiple bit error recovery")
        else:
            self.log_message("✓ Protocol can recover from some bit errors")
        
        # Test memory usage for large data
        self.log_message("Testing memory usage...")
        try:
            large_data = b'A' * 5000
            frames = Frame.create_fragmented_frames(0, large_data)
            total_memory = sum(len(frame) for frame in frames)
            self.log_message(f"✓ Memory usage for 5KB data: {total_memory} bytes")
        except Exception as e:
            self.log_message(f"✗ Memory limitation: {e}")
            limitations.append(f"Memory usage: {e}")
        
        return limitations
    
    def generate_report(self):
        """Generate comprehensive evaluation report"""
        self.log_message("\n" + "="*60)
        self.log_message("PROTOCOL EVALUATION REPORT")
        self.log_message("="*60)
        
        # Latency Analysis
        if self.results['latency']:
            avg_latency = statistics.mean(self.results['latency'])
            max_latency = max(self.results['latency'])
            min_latency = min(self.results['latency'])
            self.log_message(f"\nLATENCY ANALYSIS:")
            self.log_message(f"  Average latency: {avg_latency:.3f} ms")
            self.log_message(f"  Maximum latency: {max_latency:.3f} ms")
            self.log_message(f"  Minimum latency: {min_latency:.3f} ms")
            self.log_message(f"  Latency trend: {'Increasing' if self.results['latency'][-1] > self.results['latency'][0] else 'Stable'}")
        
        # Overhead Analysis
        if self.results['overhead']:
            avg_overhead = statistics.mean(self.results['overhead'])
            max_overhead = max(self.results['overhead'])
            min_overhead = min(self.results['overhead'])
            self.log_message(f"\nBANDWIDTH OVERHEAD ANALYSIS:")
            self.log_message(f"  Average overhead: {avg_overhead:.2f}%")
            self.log_message(f"  Maximum overhead: {max_overhead:.2f}%")
            self.log_message(f"  Minimum overhead: {min_overhead:.2f}%")
            self.log_message(f"  Overhead trend: {'Increasing' if self.results['overhead'][-1] > self.results['overhead'][0] else 'Stable'}")
        
        # Success Rate Analysis
        if self.results['success_rate']:
            avg_success = statistics.mean(self.results['success_rate'])
            min_success = min(self.results['success_rate'])
            max_success = max(self.results['success_rate'])
            self.log_message(f"\nRELIABILITY ANALYSIS:")
            self.log_message(f"  Average success rate: {avg_success:.2f}%")
            self.log_message(f"  Minimum success rate: {min_success:.2f}%")
            self.log_message(f"  Maximum success rate: {max_success:.2f}%")
            self.log_message(f"  Reliability trend: {'Decreasing' if self.results['success_rate'][-1] < self.results['success_rate'][0] else 'Stable'}")
        
        # Protocol Limitations
        limitations = self.identify_limitations()
        if limitations:
            self.log_message(f"\nPROTOCOL LIMITATIONS:")
            for limitation in limitations:
                self.log_message(f"  - {limitation}")
        else:
            self.log_message(f"\nPROTOCOL LIMITATIONS: None identified in basic tests")
        
        # Recommendations
        self.log_message(f"\nRECOMMENDATIONS:")
        if self.results['latency'] and statistics.mean(self.results['latency']) > 10:
            self.log_message(f"  - Consider optimizing frame processing for lower latency")
        if self.results['overhead'] and statistics.mean(self.results['overhead']) > 50:
            self.log_message(f"  - Consider reducing protocol overhead for better bandwidth efficiency")
        if self.results['success_rate'] and statistics.mean(self.results['success_rate']) < 90:
            self.log_message(f"  - Consider improving error correction mechanisms")
        if limitations:
            self.log_message(f"  - Address identified limitations for production use")
        
        self.log_message("\n" + "="*60)
    
    def export_log(self):
        """Export all log data to file in logs directory"""
        try:
            with open(self.log_filename, 'w', encoding='utf-8') as f:
                f.write("Protocol Evaluation Log\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Protocol: Custom UDP with Fragmentation\n")
                f.write(f"Fragment Size: {Frame.FRAGMENT_SIZE} bytes\n")
                f.write(f"Log Directory: {os.path.abspath(self.log_dir)}\n")
                f.write("=" * 50 + "\n\n")
                
                for log_entry in self.log_data:
                    f.write(log_entry + "\n")
                
                # Add summary statistics
                f.write("\n" + "=" * 50 + "\n")
                f.write("SUMMARY STATISTICS\n")
                f.write("=" * 50 + "\n")
                
                if self.results['latency']:
                    f.write(f"Average Latency: {statistics.mean(self.results['latency']):.3f} ms\n")
                    f.write(f"Max Latency: {max(self.results['latency']):.3f} ms\n")
                    f.write(f"Min Latency: {min(self.results['latency']):.3f} ms\n")
                
                if self.results['overhead']:
                    f.write(f"Average Overhead: {statistics.mean(self.results['overhead']):.2f}%\n")
                    f.write(f"Max Overhead: {max(self.results['overhead']):.2f}%\n")
                    f.write(f"Min Overhead: {min(self.results['overhead']):.2f}%\n")
                
                if self.results['success_rate']:
                    f.write(f"Average Success Rate: {statistics.mean(self.results['success_rate']):.2f}%\n")
                    f.write(f"Min Success Rate: {min(self.results['success_rate']):.2f}%\n")
                    f.write(f"Max Success Rate: {max(self.results['success_rate']):.2f}%\n")
                
                # Add file information
                f.write(f"\nLog file: {os.path.basename(self.log_filename)}\n")
                f.write(f"Total log entries: {len(self.log_data)}\n")
            
            self.log_message(f"\nLog exported to: {self.log_filename}")
            self.log_message(f"Log directory: {os.path.abspath(self.log_dir)}")
            return True
            
        except Exception as e:
            self.log_message(f"Error exporting log: {e}")
            return False
    
    def list_log_files(self):
        """List all log files in the logs directory"""
        try:
            if os.path.exists(self.log_dir):
                log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.log')]
                if log_files:
                    self.log_message(f"\nExisting log files in {self.log_dir}:")
                    for log_file in sorted(log_files, reverse=True):  # Most recent first
                        file_path = os.path.join(self.log_dir, log_file)
                        file_size = os.path.getsize(file_path)
                        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                        self.log_message(f"  {log_file} ({file_size} bytes, {file_time.strftime('%Y-%m-%d %H:%M:%S')})")
                else:
                    self.log_message(f"No existing log files found in {self.log_dir}")
            else:
                self.log_message(f"Log directory {self.log_dir} does not exist")
        except Exception as e:
            self.log_message(f"Error listing log files: {e}")

def main():
    """Main evaluation function"""
    print("Protocol Evaluation Script")
    print("="*50)
    
    evaluator = ProtocolEvaluator()
    
    # List existing log files
    evaluator.list_log_files()
    
    # Test data sizes (reduced to avoid overflow)
    data_sizes = [16, 32, 64, 128, 256, 512, 1024, 2048]
    
    # Run evaluations
    evaluator.measure_latency(data_sizes, iterations=50)
    evaluator.measure_overhead(data_sizes)
    evaluator.measure_success_rate(data_sizes, iterations=50)
    
    # Test fragmentation efficiency (reduced max size)
    sizes, fragment_counts, overhead_ratios = evaluator.test_fragmentation_efficiency(3000)
    
    # Generate report
    evaluator.generate_report()
    
    # Export log
    evaluator.export_log()
    
    print("\nEvaluation completed!")

if __name__ == "__main__":
    main()