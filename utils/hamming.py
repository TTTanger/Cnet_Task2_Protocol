def data_to_4_bits_groups(binary_data):
    '''
    Input: integer in binary format (e.g., 0b1011)
    Output: groups of 4 bits as lists of integers
    '''
    # Convert to list of bits
    bits = []
    while binary_data:
        bits.insert(0, binary_data & 1)
        binary_data >>= 1
    
    # Pad with zeros to make length multiple of 4
    padding_length = (4 - len(bits) % 4) % 4
    bits = [0] * padding_length + bits
    
    # Split into groups of 4 bits
    four_bits_groups = []
    for i in range(0, len(bits), 4):
        group = bits[i:i+4]
        four_bits_groups.append(group)
    
    return four_bits_groups

def hamming74(binary_data):
    """
    Implement (7,4) Hamming code encoding
    Input: integer in binary format (e.g., 0b1011)
    Output: integer representing binary data with hamming code
    """

    four_bits_groups = data_to_4_bits_groups(binary_data)
    encoded_binary = 0
    
    for four_bits_data in four_bits_groups:
        # Calculate parity bits
        p1 = four_bits_data[0] ^ four_bits_data[1] ^ four_bits_data[3]
        p2 = four_bits_data[0] ^ four_bits_data[2] ^ four_bits_data[3]
        p3 = four_bits_data[1] ^ four_bits_data[2] ^ four_bits_data[3]

        # Combine into 7-bit Hamming code
        hamming_bits = [
            p1,                 # Position 1
            p2,                 # Position 2
            four_bits_data[0],  # Position 3
            p3,                 # Position 4
            four_bits_data[1],  # Position 5
            four_bits_data[2],  # Position 6
            four_bits_data[3]   # Position 7
        ]
        
        # Convert to binary by shifting and combining
        for bit in hamming_bits:
            encoded_binary = (encoded_binary << 1) | bit

    return encoded_binary

def fix_hamming74_group(encoded_data):
    """
    Fix single bit errors in one 7-bit Hamming code group
    Input: 7-bit integer
    Output: (fixed_data, error_position, had_error)
    """
    # Convert to bits list
    bits = []
    for i in range(7):
        bits.insert(0, (encoded_data >> i) & 1)
    
    # Calculate syndrome
    s1 = bits[6] ^ bits[4] ^ bits[2] ^ bits[0]  # Check p1
    s2 = bits[5] ^ bits[4] ^ bits[1] ^ bits[0]  # Check p2
    s3 = bits[3] ^ bits[2] ^ bits[1] ^ bits[0]  # Check p3
    
    # Convert syndrome to error position
    error_pos = s1 + (s2 << 1) + (s3 << 2)
    
    if error_pos == 0:
        return encoded_data, 0, False
        
    # Fix error by flipping bit at error position
    error_pos = 7 - error_pos  # Convert to bit position (MSB = 0)
    fixed_data = encoded_data ^ (1 << (error_pos))
    
    return fixed_data, error_pos, True

def fix_hamming74(encoded_data):
    """
    Fix single bit errors in multiple Hamming code groups
    Input: integer containing multiple 7-bit Hamming codes
    Output: (fixed_data, error_positions, had_errors)
    """
    # Get number of 7-bit groups
    num_groups = (encoded_data.bit_length() + 6) // 7
    
    fixed_data = 0
    error_positions = []
    
    # Process each 7-bit group
    for i in range(num_groups):
        # Extract current group
        group = (encoded_data >> (i * 7)) & 0x7F
        
        # Fix errors in group
        fixed_group, error_pos, had_error = fix_hamming74_group(group)
        
        # Update results
        fixed_data |= fixed_group << (i * 7)
        if had_error:
            error_positions.append(i * 7 + error_pos)
    
    had_errors = len(error_positions) > 0
    return fixed_data, error_positions, had_errors

# Test
if __name__ == "__main__":
    data = 0b1011
    print(f"Input binary: {bin(data)[2:]}")  
    
    result = hamming74(data)
    print(f"Hamming code (binary): {bin(result)[2:].zfill(7)}")
    print(type(result))
    
    # Test with multiple groups
    data = 0b1011_0101  # Two 4-bit groups
    print(f"Input binary: {bin(data)[2:]}")
    
    # Encode
    encoded = hamming74(data)
    print(f"Encoded data: {bin(encoded)[2:].zfill(14)}")  # Should be 14 bits (2*7)
    
    # Introduce errors
    corrupted = encoded ^ (1 << 3) ^ (1 << 10)  # Errors in both groups
    print(f"Corrupted data: {bin(corrupted)[2:].zfill(14)}")
    
    # Fix errors
    fixed, positions, had_errors = fix_hamming74(corrupted)
    print(f"Fixed data: {bin(fixed)[2:].zfill(14)}")
    print(f"Error positions: {positions}")
    print(f"Had errors: {had_errors}")