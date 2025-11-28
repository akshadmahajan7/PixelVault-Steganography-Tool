from PIL import Image
import stepic
import base64
import os

def decode_data(stego_image_path, output_folder):
    # 1. Open Image
    img = Image.open(stego_image_path)
    
    # 2. Extract Data
    # Stepic reads the LSBs and returns the embedded string
    try:
        decoded_string = stepic.decode(img)
    except Exception as e:
        raise ValueError("No hidden data found or image corrupted.")

    # 3. Parse Protocol "filename|data"
    if "|" not in decoded_string:
        raise ValueError("Invalid data format. This image was not encoded by PixelVault.")
        
    filename, b64_data = decoded_string.split("|", 1)
    
    # 4. Reconstruct File
    file_bytes = base64.b64decode(b64_data)
    
    output_path = os.path.join(output_folder, f"recovered_{filename}")
    
    with open(output_path, "wb") as f:
        f.write(file_bytes)
        
    return f"Recovered file: {output_path}"
