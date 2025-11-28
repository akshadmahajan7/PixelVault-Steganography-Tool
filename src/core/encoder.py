from PIL import Image
import stepic
import base64
import os

def encode_data(cover_image_path, secret_file_path, output_path):
    # 1. Prepare the Payload
    # We prepend the filename so we know what extension to use when decoding
    filename = os.path.basename(secret_file_path)
    
    with open(secret_file_path, "rb") as f:
        file_bytes = f.read()
        
    # Convert binary to Base64 string to make it compatible with text steganography
    b64_data = base64.b64encode(file_bytes).decode('utf-8')
    
    # Create protocol string: "filename.ext|base64string"
    payload = f"{filename}|{b64_data}"
    payload_bytes = payload.encode('utf-8')

    # 2. Open Cover Image
    img = Image.open(cover_image_path).convert('RGB')
    
    # 3. Embed Data
    # Stepic embeds data into the LSB
    stego_img = stepic.encode(img, payload_bytes)
    
    # 4. Save
    # force PNG to prevent data loss
    stego_img.save(output_path, 'PNG')
    return f"Saved to {output_path}"
