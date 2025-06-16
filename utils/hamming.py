def hamming74_encode(data: bytes):
    bitstream = ''.join(f'{byte:08b}' for byte in data)
    if len(bitstream) % 4 != 0:
        bitstream += '0' * (4 - len(bitstream) % 4)

    code_bits = []
    for i in range(0, len(bitstream), 4):
        block = bitstream[i:i+4]
        code_bits.extend(hamming74_encode_block(block))

    encoded_bytes = bytearray()
    for i in range(0, len(code_bits), 8):
        byte_bits = code_bits[i:i+8]
        if len(byte_bits) < 8:
            byte_bits += [0] * (8 - len(byte_bits)) 
        byte_str = ''.join(str(b) for b in byte_bits)
        encoded_bytes.append(int(byte_str, 2))

    return bytes(encoded_bytes), len(data)

def hamming74_encode_block(block4):
    d = [int(b) for b in block4]  # d0, d1, d2, d3
    # Hamming(7,4): p0, p1, d0, p2, d1, d2, d3
    p0 = d[0] ^ d[1] ^ d[3]
    p1 = d[0] ^ d[2] ^ d[3]
    p2 = d[1] ^ d[2] ^ d[3]
    return [p0, p1, d[0], p2, d[1], d[2], d[3]]

def hamming74_decode_block(block7):
    bits = [int(b) for b in block7]
    # p0, p1, d0, p2, d1, d2, d3

    p1, p2, d0, p4, d1, d2, d3 = bits

    s1 = p1 ^ d0 ^ d1 ^ d3  # p1 covers 1,3,5,7
    s2 = p2 ^ d0 ^ d2 ^ d3  # p2 covers 2,3,6,7
    s4 = p4 ^ d1 ^ d2 ^ d3  # p4 covers 4,5,6,7

    error_position = (s4 << 2) | (s2 << 1) | s1

    # Fix if error
    if error_position != 0:
        error_index = error_position - 1  # From 1-based to 0-based index
        bits[error_index] ^= 1  # Flip the error bit

    # Extract data bits
    return bits[2], bits[4], bits[5], bits[6]


def hamming74_decode(data: bytes, original_length: int):
    bitstream = ''.join(f'{byte:08b}' for byte in data)
    # Padding with zeros to make the length a multiple of 7
    if len(bitstream) % 7 != 0:
        bitstream += '0' * (7 - len(bitstream) % 7)

    decoded_bits = []
    for i in range(0, len(bitstream), 7):
        block = bitstream[i:i+7]
        d0, d1, d2, d3 = hamming74_decode_block(block)
        decoded_bits.extend([d0, d1, d2, d3])

    # Each 8 bits combine to a byte
    decoded_bytes = bytearray()
    for i in range(0, len(decoded_bits), 8):
        byte_bits = decoded_bits[i:i+8]
        # If the byte is not complete, pad with zeros
        if len(byte_bits) < 8:
            byte_bits += [0] * (8 - len(byte_bits))
        byte_str = ''.join(str(b) for b in byte_bits)
        decoded_bytes.append(int(byte_str, 2))

    return bytes(decoded_bytes[:original_length])

# Test
if __name__ == '__main__':
    data = 'hello'.encode('ascii')
    encoded, original_len = hamming74_encode(data)
    print('Encoded:', encoded)
    decoded_data = hamming74_decode(encoded, original_len)
    print('Decoded:', decoded_data)
    print('Original:', decoded_data.decode('ascii'))