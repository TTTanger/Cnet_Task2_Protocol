'''Encode part'''
def encode(data: bytes, seq_num: int) -> bytes:
    """
    Encodes the given data into a frame with Hamming(7,4) encoding and CRC-16.

    Args:
        data: original data (bytes)
        seq_num: sequence number (int)

    Returns:
        Encoded frame (bytes)
    """
    bitstream = bytes_to_bitstring(data)
    bit_len = len(bitstream)  # Length of the bitstream

    hamming_bits = hamming74_encode(bitstream)

    # Add length of the bitstream as a 2-byte field
    bit_len_bytes = bit_len.to_bytes(2, 'big')

    seq_bits = f"{seq_num:08b}"
    payload_bits = seq_bits + hamming_bits
    crc_value = calc_crc(payload_bits)

    crc_bytes = crc_value.to_bytes(2, 'big')

    hamming_bytes = int(hamming_bits, 2).to_bytes((len(hamming_bits) + 7) // 8, 'big')

    frame = bytes([seq_num]) + bit_len_bytes + hamming_bytes + crc_bytes
    return frame            


def bytes_to_bitstring(data: bytes) -> str:
    return ''.join(f"{byte:08b}" for byte in data)

def hamming74_encode(bits: str) -> str:
    def encode_block(block):
        d = list(map(int, block.ljust(4, '0')))
        p1 = d[0] ^ d[1] ^ d[3]
        p2 = d[0] ^ d[2] ^ d[3]
        p3 = d[1] ^ d[2] ^ d[3]
        return f"{p1}{p2}{d[0]}{p3}{d[1]}{d[2]}{d[3]}"
    
    return ''.join(encode_block(bits[i:i+4]) for i in range(0, len(bits), 4))

def calc_crc(bitstring: str, poly: int = 0x8005) -> int:
    # Bits to bytes conversion
    data = int(bitstring, 2).to_bytes((len(bitstring) + 7) // 8, 'big')
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc


'''Decode part'''
from typing import Tuple
def decode(frame: bytes) -> Tuple[bytes, int, bool]:
    """
    Decodes the given frame, checks for errors, and returns the original data.
    Args:
        frame: encoded frame (bytes)

    Returns:
        Tuple containing:
            - Original data (bytes)
            - Sequence number (int)
            - Error flag (bool): True if error detected, False otherwise
    """
    seq_num = frame[0]
    bit_len = int.from_bytes(frame[1:3], 'big')
    crc_received = int.from_bytes(frame[-2:], 'big')
    hamming_bytes = frame[3:-2]
    hamming_bits = ''.join(f"{byte:08b}" for byte in hamming_bytes)

    seq_bits = f"{seq_num:08b}"
    payload_bits = seq_bits + hamming_bits
    crc_calculated = calc_crc(payload_bits)

    if crc_calculated != crc_received:
        return b'', seq_num, True

    # Hamming decoding
    decoded_bits, has_uncorrectable = hamming74_decode(hamming_bits)

    # Trim to original bit length
    decoded_bits = decoded_bits[:bit_len]  
    if has_uncorrectable:
        return b'', seq_num, True  # Uncorrectable error detected

    data = bitstring_to_bytes(decoded_bits)
    return data, seq_num, False                                                         

def hamming74_decode(bits: str) -> Tuple[str, bool]:
    corrected = ''
    uncorrectable = False
    for i in range(0, len(bits), 7):
        block = bits[i:i+7]
        if len(block) < 7:
            break # Ignore incomplete blocks
        b = list(map(int, block))
        # syndrome
        s1 = b[0] ^ b[2] ^ b[4] ^ b[6]
        s2 = b[1] ^ b[2] ^ b[5] ^ b[6]
        s3 = b[3] ^ b[4] ^ b[5] ^ b[6]
        syndrome = (s1 << 2) | (s2 << 1) | s3
        if syndrome != 0:
            if 1 <= syndrome <= 7:
                b[syndrome - 1] ^= 1  
            else:
                uncorrectable = True
        corrected += f"{b[2]}{b[4]}{b[5]}{b[6]}"
    return corrected, uncorrectable

def bitstring_to_bytes(bits: str) -> bytes:
    if len(bits) % 8 != 0:
        bits = bits[:-(len(bits) % 8)] 
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
