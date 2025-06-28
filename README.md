# Customized UDP Reliable Protocol

A Python implementation of a custom reliable protocol built on top of UDP, featuring multi-layered error handling with CRC-16 error detection, Hamming(7,4) error correction, and intelligent message fragmentation.

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
│ Seq Num │ Fragment ID  │ Encoded Data     │ Origingal Len   │ CRC-16  │
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

The evaluation script provides comprehensive analysis:

### Performance Metrics
- **Latency**: Typically <1ms for small messages
- **Overhead**: 80-85% for typical messages
- **Success Rate**: >99% for single-bit errors, >98% for large messages

### Log Files
- Automatically created in `logs/` directory
- Timestamped filenames (e.g., `protocol_evaluation_20241201_143022.log`)
- Include detailed performance statistics
- Contain protocol limitation analysis

### Sample Output
```
=== Latency Measurement ===
Data size:     16 bytes | Avg latency: 0.245 ms | Std dev: 0.089 ms
Data size:    256 bytes | Avg latency: 0.312 ms | Std dev: 0.102 ms

=== Bandwidth Overhead Measurement ===
Data size:     16 bytes | Frame size:     29 bytes | Overhead:   13 bytes ( 81.25%)
Data size:    256 bytes | Frame size:    448 bytes | Overhead:  192 bytes ( 75.00%)

=== Success Rate Measurement ===
Data size:     16 bytes | Success:  99.50% | CRC errors:   0.30% | Frame errors:   0.20%
Data size:    256 bytes | Success:  98.80% | CRC errors:   0.90% | Frame errors:   0.30%
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

## Limitations

- **Sequence Numbers**: 8-bit limit (256 unique sequences)
- **Fragment Size**: Fixed 16-byte size
- **Memory Usage**: In-memory fragment buffering
- **Concurrency**: Single connection per instance

## Future Improvements

- Adaptive fragmentation based on error rates
- Selective repeat retransmission protocol
- Flow control mechanisms
- Multiple concurrent connection support

## Requirements

- Python 3.6+
- Standard library modules (socket, threading, time, statistics)
- No external dependencies

## License

This project is for educational purposes and demonstrates reliable protocol implementation over UDP.