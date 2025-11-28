import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import sys
import threading

# --- PATH SETUP ---
# Ensure we can import from src/ even if running from root
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import Backend Logic
from src.core.encoder import encode_data
from src.core.decoder import decode_data
from src.utils.file_handler import check_capacity

# --- CONFIGURATION ---
ctk.set_appearance_mode("Dark")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue", "green", "dark-blue"

class PixelVaultApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        
        # Initialize Drag and Drop mechanism
        self.TkdndVersion = TkinterDnD._require(self)
        
        # Window Setup
        self.title("PixelVault // Stealth Operations")
        self.geometry("700x600")
        self.resizable(False, False)
        
        # Grid Layout: 1 Column, Header + Tabs + Status
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ===================================================
        # 1. HEADER SECTION (Logo + Title)
        # ===================================================
        self.header_frame = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color="#1a1a1a")
        self.header_frame.grid(row=0, column=0, sticky="ew")
        
        # Locate Logo
        current_dir = os.path.dirname(os.path.abspath(__file__)) # gui/
        project_root = os.path.dirname(current_dir)              # root/
        logo_path = os.path.join(project_root, "assets", "logo2.png")

        try:
            # Load and Resize Image
            img_data = Image.open(logo_path)
            self.logo_image = ctk.CTkImage(light_image=img_data, 
                                           dark_image=img_data, 
                                           size=(40, 40)) 
            
            # Label with Image AND Text
            self.logo_label = ctk.CTkLabel(self.header_frame, 
                                           text="  PIXELVAULT", 
                                           image=self.logo_image,
                                           compound="left", 
                                           font=ctk.CTkFont(family="Roboto Medium", size=24))
        except Exception:
            # Fallback if image is missing
            print(f"Warning: Logo not found at {logo_path}")
            self.logo_label = ctk.CTkLabel(self.header_frame, 
                                           text="🕵️ PIXELVAULT", 
                                           font=ctk.CTkFont(family="Roboto Medium", size=24))

        self.logo_label.pack(pady=20)

        # ===================================================
        # 2. MAIN TABS
        # ===================================================
        self.tab_view = ctk.CTkTabview(self, width=650, height=420)
        self.tab_view.grid(row=1, column=0, padx=20, pady=20)
        
        self.tab_enc = self.tab_view.add("  🔒 ENCRYPT & HIDE  ")
        self.tab_dec = self.tab_view.add("  🔓 EXTRACT DATA  ")

        self.setup_encode_ui()
        self.setup_decode_ui()

        # ===================================================
        # 3. STATUS BAR
        # ===================================================
        self.status_bar = ctk.CTkLabel(self, text="System Ready... Waiting for input.", 
                                       text_color="gray", anchor="w")
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))


    def setup_encode_ui(self):
        """UI Elements for the Encoding Tab"""
        # -- Cover Image --
        self.lbl_cover = ctk.CTkLabel(self.tab_enc, text="1. Cover Image (Container)", 
                                      font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_cover.pack(pady=(15, 5), anchor="w", padx=20)
        
        self.entry_cover = ctk.CTkEntry(self.tab_enc, placeholder_text="Drag & Drop PNG/JPG/BMP here...", width=500)
        self.entry_cover.pack(pady=5, padx=20)
        
        # Drag & Drop Bindings
        self.entry_cover.drop_target_register(DND_FILES)
        self.entry_cover.dnd_bind('<<Drop>>', lambda e: self.on_drop(e, self.entry_cover))

        # -- Secret File --
        self.lbl_secret = ctk.CTkLabel(self.tab_enc, text="2. Secret Payload (PDF/TXT)", 
                                       font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_secret.pack(pady=(20, 5), anchor="w", padx=20)
        
        self.entry_secret = ctk.CTkEntry(self.tab_enc, placeholder_text="Drag & Drop Secret File here...", width=500)
        self.entry_secret.pack(pady=5, padx=20)
        
        self.entry_secret.drop_target_register(DND_FILES)
        self.entry_secret.dnd_bind('<<Drop>>', lambda e: self.on_drop(e, self.entry_secret))

        # -- Action Button --
        self.btn_encode = ctk.CTkButton(self.tab_enc, text="EXECUTE STEGANOGRAPHY", 
                                        width=200, height=40, corner_radius=20,
                                        fg_color="#2cc985", hover_color="#229964",
                                        font=ctk.CTkFont(weight="bold"),
                                        command=self.start_encoding_thread)
        self.btn_encode.pack(pady=40)

    def setup_decode_ui(self):
        """UI Elements for the Decoding Tab"""
        self.lbl_stego = ctk.CTkLabel(self.tab_dec, text="Source Image (Encoded)", 
                                      font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_stego.pack(pady=(30, 5), anchor="w", padx=20)
        
        self.entry_stego = ctk.CTkEntry(self.tab_dec, placeholder_text="Drag Encoded Image here...", width=500)
        self.entry_stego.pack(pady=5, padx=20)
        
        self.entry_stego.drop_target_register(DND_FILES)
        self.entry_stego.dnd_bind('<<Drop>>', lambda e: self.on_drop(e, self.entry_stego))

        self.btn_decode = ctk.CTkButton(self.tab_dec, text="RETRIEVE DATA", 
                                        width=200, height=40, corner_radius=20,
                                        fg_color="#3B8ED0", hover_color="#2C6E9F",
                                        font=ctk.CTkFont(weight="bold"),
                                        command=self.start_decoding_thread)
        self.btn_decode.pack(pady=50)

    # ===================================================
    # LOGIC & EVENTS
    # ===================================================

    def on_drop(self, event, entry_widget):
        """Handles file drop: Cleans path and flashes entry border"""
        file_path = event.data.strip('{}') # Remove braces added by Windows
        entry_widget.delete(0, "end")
        entry_widget.insert(0, file_path)
        
        # Visual Flash Effect
        original_color = entry_widget.cget("border_color")
        entry_widget.configure(border_color="#2cc985") # Flash Green
        self.after(500, lambda: entry_widget.configure(border_color=original_color))

    def start_encoding_thread(self):
        """Starts encoding in a separate thread to keep UI responsive"""
        threading.Thread(target=self.run_encode, daemon=True).start()

    def run_encode(self):
        cover = self.entry_cover.get()
        secret = self.entry_secret.get()
        
        if not cover or not secret:
            self.status_bar.configure(text="⚠️ Error: Missing files", text_color="#FF5555")
            return

        # Disable UI
        self.btn_encode.configure(state="disabled", text="Processing...")
        self.status_bar.configure(text="⏳ Analyzing image capacity...", text_color="yellow")

        try:
            # 1. Check Capacity
            check_capacity(cover, secret)
            self.status_bar.configure(text="⏳ Encrypting & Embedding...", text_color="yellow")
            
            # 2. Get Save Location (Requires main thread for dialog, but works in simple tkinter)
            # Ideally, use after() for thread safety, but direct call works in most OS for file dialogs
            output = filedialog.asksaveasfilename(defaultextension=".png", 
                                                  filetypes=[("PNG Image", "*.png")])
            if output:
                res = encode_data(cover, secret, output)
                self.status_bar.configure(text=f"✅ {res}", text_color="#2cc985")
                messagebox.showinfo("Mission Success", "Data successfully hidden in image.")
            else:
                self.status_bar.configure(text="❌ Operation Cancelled", text_color="gray")

        except Exception as e:
            self.status_bar.configure(text=f"❌ Error: {str(e)}", text_color="#FF5555")
            messagebox.showerror("Error", str(e))
        
        finally:
            self.btn_encode.configure(state="normal", text="EXECUTE STEGANOGRAPHY")

    def start_decoding_thread(self):
        threading.Thread(target=self.run_decode, daemon=True).start()

    def run_decode(self):
        stego = self.entry_stego.get()
        if not stego:
            self.status_bar.configure(text="⚠️ Error: Missing image", text_color="#FF5555")
            return

        self.btn_decode.configure(state="disabled", text="Extracting...")
        self.status_bar.configure(text="⏳ Analyzing pixel data...", text_color="yellow")
        
        try:
            output_folder = filedialog.askdirectory()
            if output_folder:
                res = decode_data(stego, output_folder)
                self.status_bar.configure(text=f"✅ Data Recovered", text_color="#3B8ED0")
                messagebox.showinfo("Success", res)
            else:
                self.status_bar.configure(text="❌ Operation Cancelled", text_color="gray")
        except Exception as e:
            self.status_bar.configure(text=f"❌ Decryption Failed: {str(e)}", text_color="#FF5555")
            messagebox.showerror("Failed", str(e))
        finally:
            self.btn_decode.configure(state="normal", text="RETRIEVE DATA")

if __name__ == "__main__":
    app = PixelVaultApp()
    app.mainloop()
