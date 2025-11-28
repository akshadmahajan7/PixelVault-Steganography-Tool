import os
import sys
import uuid
import shutil
from flask import Flask, render_template, request, send_file, jsonify, after_this_request

# --- PATH CONFIGURATION ---
# We need to add the project root to sys.path so we can import 'src'
# structure:
# root/
#   src/
#   web/
#     app.py
current_dir = os.path.dirname(os.path.abspath(__file__)) # .../web
project_root = os.path.dirname(current_dir)              # .../PixelVault-Steganography
sys.path.append(project_root)

# Import our custom backend logic
try:
    from src.core.encoder import encode_data
    from src.core.decoder import decode_data
    from src.utils.file_handler import check_capacity
except ImportError as e:
    print("CRITICAL ERROR: Could not import backend modules.")
    print(f"Make sure you are running this from the project root or check sys.path. Error: {e}")
    sys.exit(1)

app = Flask(__name__)

# --- SERVER CONFIGURATION ---
UPLOAD_FOLDER = os.path.join(current_dir, 'temp_uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # Limit uploads to 32MB to prevent DoS

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Serves the main HTML interface."""
    return render_template('index.html')

@app.route('/api/encode', methods=['POST'])
def encode():
    """
    Handles the Encryption and Hiding process.
    1. Creates a unique session ID.
    2. Validates capacity.
    3. Embeds data.
    4. Returns the PNG image.
    5. Self-destructs temp files.
    """
    # 1. Create Isolation Session
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_dir, exist_ok=True)

    try:
        # 2. Retrieve Files
        cover_file = request.files.get('cover_image')
        secret_file = request.files.get('secret_file')

        if not cover_file or not secret_file:
            return jsonify({'error': 'Missing cover image or secret file.'}), 400

        # Save to temp session
        cover_path = os.path.join(session_dir, "cover_input.png") # Normalize name
        secret_filename = secret_file.filename or "secret.txt" # Keep original extension
        secret_path = os.path.join(session_dir, secret_filename)
        output_path = os.path.join(session_dir, "secure_output.png")

        cover_file.save(cover_path)
        secret_file.save(secret_path)

        # 3. Logic Checks
        # Verify the image is large enough to hold the secret
        check_capacity(cover_path, secret_path)

        # 4. Execute Steganography
        encode_data(cover_path, secret_path, output_path)

        # 5. Cleanup Hook
        # This runs AFTER the file is sent to the user
        @after_this_request
        def cleanup(response):
            try:
                shutil.rmtree(session_dir)
                print(f"[SECURE DELETE] Session {session_id} wiped.")
            except Exception as e:
                print(f"[ERROR] Cleanup failed for {session_id}: {e}")
            return response

        # 6. Send Response
        return send_file(
            output_path, 
            as_attachment=True, 
            download_name="pixelvault_secure.png", 
            mimetype='image/png'
        )

    except Exception as e:
        # Immediate cleanup on error
        shutil.rmtree(session_dir, ignore_errors=True)
        print(f"[ERROR] Encoding failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/decode', methods=['POST'])
def decode():
    """
    Handles the Extraction process.
    1. Receives stego-image.
    2. Extracts hidden bits.
    3. Reconstructs original file.
    4. Returns the file.
    """
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_dir, exist_ok=True)

    try:
        # 1. Retrieve Image
        stego_file = request.files.get('stego_image')
        if not stego_file:
            return jsonify({'error': 'Missing encoded image.'}), 400

        stego_path = os.path.join(session_dir, "stego_input.png")
        stego_file.save(stego_path)

        # 2. Prepare Extraction Folder
        extract_dir = os.path.join(session_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        # 3. Execute Logic
        # decode_data writes the file(s) into extract_dir
        decode_data(stego_path, extract_dir)
        
        # 4. Find the extracted file
        # We don't know the name yet, so we list the directory
        files = os.listdir(extract_dir)
        if not files:
            raise Exception("No data found inside image. Was it created by PixelVault?")
            
        recovered_filename = files[0] # Take the first file found
        recovered_path = os.path.join(extract_dir, recovered_filename)

        # 5. Cleanup Hook
        @after_this_request
        def cleanup(response):
            try:
                shutil.rmtree(session_dir)
                print(f"[SECURE DELETE] Session {session_id} wiped.")
            except Exception as e:
                print(f"[ERROR] Cleanup failed: {e}")
            return response

        # 6. Send Back the Secret
        return send_file(
            recovered_path, 
            as_attachment=True, 
            download_name=recovered_filename
        )

    except Exception as e:
        shutil.rmtree(session_dir, ignore_errors=True)
        print(f"[ERROR] Decoding failed: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run on all interfaces (0.0.0.0) so you can access it from mobile/other PCs if needed
    print(f"[*] PixelVault Server initialized...")
    print(f"[*] Temp folder: {UPLOAD_FOLDER}")
    app.run(debug=True, host='0.0.0.0', port=5000)
