# Customized UDP Reliable Protocol

A Python implementation of a custom reliable protocol built on top of UDP, featuring multi-layered error handling with CRC-16 error detection, Hamming(7,4) error correction, and intelligent message fragmentation.

**Based on comprehensive evaluation testing, the protocol demonstrates moderate reliability (67.75% average success rate) with significant overhead (85.89% average) and reasonable latency performance (5.736ms average).**

## Features

- **Error Detection**: CRC-16 checksum for frame integrity
- **Error Correction**: Hamming(7,4) code for single-bit error correction
- **Message Fragmentation**: Automatic fragmentation for large messages (16-byte fragments)
- **Reliable Delivery**: Sequence numbers, acknowledgments, and retransmission
- **Performance Evaluation**: Comprehensive testing and analysis tools

## Project Structure

```
Ex2 SW/
├── protocol.py          # Core protocol implementation
├── udp_client.py        # UDP client with reliable protocol
├── udp_server.py        # UDP server with reliable protocol
├── lossy_channel.py     # Network simulation with errors
├── evaluate.py          # Protocol evaluation and testing
├── utils/
│   ├── crc.py          # CRC-16 implementation
│   └── hamming.py      # Hamming(7,4) error correction
└── logs/               # Evaluation logs (auto-created)
```

## File Descriptions

### Core Protocol Files

#### `protocol.py`
The main protocol implementation containing the `Frame` class that handles:
- Frame creation with headers, data encoding, and CRC calculation
- Automatic message fragmentation (16-byte fragments)
- Frame validation and error checking
- Hamming(7,4) encoding/decoding integration

#### `udp_client.py`
UDP client implementation featuring:
- Dual-threaded architecture (send/receive)
- Automatic message fragmentation for large data
- Fragment buffering and reassembly
- Retransmission with timeout (1s) and retry limit (10)
- Sequence number management

#### `udp_server.py`
UDP server implementation with identical features to the client:
- Bidirectional communication capability
- Fragment handling and reassembly
- Automatic ACK generation
- Error recovery mechanisms

### Utility Files

#### `utils/crc.py`
CRC-16 implementation using polynomial 0x8005:
- Bit-by-bit CRC calculation
- Frame integrity verification
- Standard CRC-16 algorithm

#### `utils/hamming.py`
Hamming(7,4) error correction code:
- Encodes 4 data bits into 7 bits with 3 parity bits
- Single-bit error detection and correction
- Double-bit error detection
- Block-based encoding/decoding

#### `lossy_channel.py`
Network simulation module:
- Simulates bit errors (0.05% per bit)
- Simulates packet loss (0.01% per byte)
- Realistic network condition testing

### Evaluation and Testing

#### `evaluate.py`
Comprehensive protocol evaluation script that measures:

**Performance Metrics:**
- **Latency**: End-to-end transmission time
- **Bandwidth Overhead**: Protocol efficiency analysis
- **Success Rate**: Error handling effectiveness
- **Fragmentation Efficiency**: Large message handling

**Testing Features:**
- Automated testing with configurable parameters
- Log generation with timestamps
- Performance trend analysis
- Protocol limitation identification
- Export results to timestamped log files

**Usage:**
```bash
python evaluate.py
```

**Output:**
- Console output with real-time results
- Detailed log file in `logs/` directory
- Performance statistics and recommendations
- Protocol limitation analysis

## Quick Start

### 1. Start the Server
```bash
python udp_server.py
```

### 2. Start the Client
```bash
python udp_client.py
```

### 3. Send Messages
- Type normal messages for small data testing
- Type `test_large` for fragmentation testing

### 4. Run Evaluation
```bash
python evaluate.py
```

## Protocol Specifications

### Frame Format
```
┌─────────┬──────────────┬──────────────────┬─────────────────┬─────────┐
│ Seq Num │ Fragment ID  │ Encoded Data     │ Original Len    │ CRC-16  │
│ (1 byte)│   (2 bytes)  │ (Hamming 7,4)    │ (2 bytes)       │(2 bytes)│
└─────────┴──────────────┴──────────────────┴─────────────────┴─────────┘
```

### Key Parameters
- **Fragment Size**: 16 bytes
- **Timeout**: 1 second
- **Max Retries**: 10
- **Sequence Numbers**: 8-bit (0-255)
- **CRC Polynomial**: 0x8005

## Evaluation Results

The evaluation script provides comprehensive analysis based on real-world testing:

### Performance Metrics
- **Latency**: 0.270ms - 22.760ms (5.736ms average)
- **Overhead**: 75.34% - 118.75% (85.89% average)
- **Success Rate**: 10.00% - 96.00% (67.75% average)

### Detailed Performance Data

**Latency Performance:**
- 16 bytes: 0.270ms average latency
- 32 bytes: 0.532ms average latency
- 64 bytes: 0.811ms average latency
- 128 bytes: 1.600ms average latency
- 256 bytes: 2.960ms average latency
- 512 bytes: 5.604ms average latency
- 1024 bytes: 11.349ms average latency
- 2048 bytes: 22.760ms average latency

**Bandwidth Overhead:**
- 16 bytes: 118.75% overhead (35 bytes total)
- 32 bytes: 96.88% overhead (63 bytes total)
- 64 bytes: 85.94% overhead (119 bytes total)
- 128 bytes: 80.47% overhead (231 bytes total)
- 256 bytes: 77.73% overhead (455 bytes total)
- 512 bytes: 76.37% overhead (903 bytes total)
- 1024 bytes: 75.68% overhead (1799 bytes total)
- 2048 bytes: 75.34% overhead (3591 bytes total)

**Success Rate Performance:**
- 16 bytes: 96.00% success rate
- 32 bytes: 96.00% success rate
- 64 bytes: 94.00% success rate
- 128 bytes: 90.00% success rate
- 256 bytes: 74.00% success rate
- 512 bytes: 50.00% success rate
- 1024 bytes: 32.00% success rate
- 2048 bytes: 10.00% success rate

**Fragmentation Efficiency:**
- 1000 bytes: 63 fragments, 119.10% overhead
- 2000 bytes: 125 fragments, 118.75% overhead
- 3000 bytes: 188 fragments, 118.87% overhead

### Log Files
- Automatically created in `logs/` directory
- Timestamped filenames (e.g., `protocol_evaluation_20250628_202604.log`)
- Include detailed performance statistics
- Contain protocol limitation analysis

### Sample Output
```
=== Latency Measurement ===
Data size:     16 bytes | Avg latency: 0.270 ms | Std dev: 0.443 ms
Data size:    256 bytes | Avg latency: 2.960 ms | Std dev: 0.697 ms

=== Bandwidth Overhead Measurement ===
Data size:     16 bytes | Frame size:     35 bytes | Overhead:   19 bytes (118.75%)
Data size:    256 bytes | Frame size:    455 bytes | Overhead:  199 bytes ( 77.73%)

=== Success Rate Measurement ===
Data size:     16 bytes | Success:  96.00% | CRC errors:   4.00% | Frame errors:   0.00%
Data size:    256 bytes | Success:  74.00% | CRC errors:  26.00% | Frame errors:   0.00%
```

## Error Handling

### Single-Bit Errors
- **Detection**: 100% with Hamming(7,4)
- **Correction**: 100% automatic correction
- **No Retransmission**: Required

### Multi-Bit Errors
- **Detection**: CRC-16 validation
- **Action**: Automatic retransmission
- **Recovery**: Fragment-level retransmission

### Packet Loss
- **Detection**: Timeout mechanism
- **Action**: Retransmission with exponential backoff
- **Limit**: Maximum 10 retries per fragment

## Identified Limitations

**Critical Issues Found Through Testing:**
- **Fragment ID Overflow**: "int too big to convert" error for large fragment counts
- **Multiple Bit Error Recovery**: Protocol cannot recover from multiple bit errors
- **Success Rate Degradation**: Performance drops significantly for large messages (>512 bytes)
- **High Overhead**: 85.89% average overhead reduces bandwidth efficiency

**Design Limitations:**
- **Sequence Numbers**: 8-bit limit (256 unique sequences)
- **Fragment Size**: Fixed 16-byte size (not adaptive)
- **Memory Usage**: In-memory fragment buffering
- **Concurrency**: Single connection per instance

## Future Improvements

**Critical Fixes:**
- **Fragment ID Handling**: Implement proper integer overflow handling for fragment IDs
- **Enhanced Error Correction**: Implement Reed-Solomon or BCH codes for multiple bit error correction
- **Adaptive Fragment Size**: Dynamic fragment size based on error rates and message size
- **Selective Repeat**: More efficient retransmission protocol for large messages

**Performance Optimizations:**
- **Reduced Protocol Overhead**: Optimize frame structure to reduce per-frame overhead
- **Flow Control**: Window-based transmission control
- **Connection Multiplexing**: Support for multiple concurrent connections
- **Compression**: Data compression to offset Hamming encoding overhead

**Reliability Enhancements:**
- **Forward Error Correction**: Implement stronger error correction codes
- **Hybrid ARQ**: Combine automatic repeat request with forward error correction
- **Quality of Service**: Different reliability levels based on message importance

## Requirements

- Python 3.6+
- Standard library modules (socket, threading, time, statistics)
- No external dependencies

## License

This project is for educational purposes and demonstrates reliable protocol implementation over UDP.