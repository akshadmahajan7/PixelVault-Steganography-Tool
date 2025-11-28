# 🕵️ PixelVault: Steganography Tool

---

## 🌟 Project Overview
**PixelVault** is a specialized privacy tool designed to secure sensitive communication through **Steganography**. Unlike encryption, which hides the contents of a message, this tool hides the existence of the message itself by embedding binary data into the noise of an image file.

The application utilizes the $\text{Least Significant Bit (LSB)}$ technique, modifying the last bit of pixel byte data. It allows users to embed not just raw text, but entire files (like $\text{.txt}$ documents or sensitive $\text{.pdf}$ reports) inside standard images without altering their visual appearance.

---

## ✨ Features and Technology Stack
| Component | Technology | Description | 
| --- | --- | --- |
| Core Language | $\text{Python 3.x}$ | The backend logic and processing engine. | 
| Image Processing | $\text{Pillow (PIL)}$ | Handles image manipulation (opening, pixel modification, saving). | 
| Steganography Logic | $\text{stepic}$ | Used for byte-level data embedding into $\text{RGBA}$ images. | 
| GUI Framework | $\text{tkinter}$ & $\text{tkinterdnd2}$ | Provides the desktop interface and drag-and-drop functionality.| 
| Cover Medias | $\text{PNG}$, $\text{BMP}$, $\text{JPEG}$ | Supports standard image formats as inputs. ($\text{JPEG}$ converted to $\text{PNG}$ on save to prevent data loss). | 
| Secret Payload | $\text{TXT}$, $\text{PDF}$, $\test{Raw Text}$ | Capable of ingesting text files and PDF documents, converting them to binary, and embedding them. | 

---

## 🛡️ Technical Implementation: The LSB Method

This tool operates on the principle that the last bit of a pixel's color value contributes the least to its visual representation.
1. Encoding (Hiding)
   * Payload Processing: The system reads the input file ($\text{.txt}$ or $\text{.pdf}$) as a raw byte stream.
   * Capacity Check: It calculates if the cover image has enough pixels to hold the file ($FileBytes \times 8 < TotalPixels \times 3$).
   * Embedding: The algorithm replaces the Least Significant Bit ($2^0$) of the pixel's color byte with bits from the file.
   * Example: If a Red pixel value is $140$ ($1000110\mathbf{0}_2$) and the file bit is $1$, the pixel becomes $141$ ($1000110\mathbf{1}_2$).

2. Decoding (Extracting)
   * The system scans the image pixels to extract the LSBs.
   * The binary stream is reconstructed and written back to a file format (e.g., `secret_recovered.pdf`).
  
---

## 📁 Project Structure
```
PixelVault-Steganography/
├── src/
│   ├── core/
│   │   ├── encoder.py        # Logic to convert text to binary and embed in pixels.
│   │   └── decoder.py        # Logic to extract binary from pixels and reconstruct text.
│   └── utils/
│       └── file_handler.py   # Helpers for file I/O and format validation.
├── gui/
│   ├── app.py                # Main tkinter application window and loop.
│   └── components/
│       └── drag_drop.py      # Implementation of Drag-and-Drop widget events.
├── assets/
│   └── logo.png              # Application icon/logo.
├── main.py                   # Entry point for the application.
├── requirements.txt          # Dependency list.
├── README.md                 # Project documentation.
└── LICENSE                   # MIT License.
```

---

## 🚀 Getting Started

### Prerequisites

* $\text{Python 3.8+}$
* $\text{pip}$ package manager

### Installation

1. Clone the repository:
```Bash
git clone https://github.com/your-username/PixelVault.git
cd PixelVault
```

2. Create a virtual environment:

```Bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:

```Bash
pip install -r requirements.txt
```

### Usage

1. Run the application:
```Bash
python main.py
```

2. **To Encode:** Drag a generic $\text{PNG}$ image into the "Cover Image" box, type your secret text, and click "Encode". Save the resulting image.
3. **To Decode:** Drag the encoded image into the tool and click "Decode" to reveal the hidden text.

---

## 🤝 Contributing

Contributions are welcome! Here are a few ways you can help improve PixelVault:
* **Cryptography Integration:** Modify `src/core/encoder.py` to encrypt the message using $\text{AES-256}$ before embedding it into the image.
* **Capacity Analysis:** Add a visual indicator in the GUI showing how many characters can fit in the loaded image based on its resolution ($TotalPixels \times 3$ bits).
* **File Hiding:** Extend functionality to hide small files ($\text{.zip}$, $\text{.txt}$) rather than just raw text strings.

---

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).
