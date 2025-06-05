import random

def lossy(data: bytes) -> bytes:
    # Convert to bytearray for mutable operations
    data_array = bytearray(data)
    
    # Use reverse iteration to safely remove elements
    i = len(data_array) - 1
    while i >= 0:
        if random.random() < 0.01:  
            del data_array[i]
        elif random.random() < 0.05:  
            bit_pos = random.randint(0, 7)
            data_array[i] ^= (1 << bit_pos)
        i -= 1
    
    return bytes(data_array)

if __name__ == "__main__":
    # Test with binary data
    try:
        # Create sample binary data
        test_data = bytes([1, 2, 3, 4, 5])
        result = lossy(test_data)
        
        print(f"Original bytes: {test_data.hex()}")
        print(f"Modified bytes: {result.hex()}")
        print(f"Original length: {len(test_data)}")
        print(f"Modified length: {len(result)}")
        
    except Exception as e:
        print(f"Error: {e}")