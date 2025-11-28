import os
from PIL import Image

def get_image_capacity(image_path):
    """
    Returns the maximum bytes that can be hidden in the image.
    Formula: (Width * Height * 3 channels) / 8 bits
    """
    img = Image.open(image_path)
    width, height = img.size
    # 3 color channels (R, G, B) allow 3 bits per pixel
    max_bytes = (width * height * 3) // 8
    return max_bytes

def check_capacity(image_path, secret_file_path):
    """
    Verifies if the secret file fits inside the cover image.
    """
    image_cap = get_image_capacity(image_path)
    secret_size = os.path.getsize(secret_file_path)
    
    # Base64 expansion factor is roughly 1.33x, adding safety margin
    required_space = int(secret_size * 1.4) 
    
    if required_space > image_cap:
        raise ValueError(f"Image too small! Capacity: {image_cap/1024:.2f}KB. Required: {required_space/1024:.2f}KB")
    return True
