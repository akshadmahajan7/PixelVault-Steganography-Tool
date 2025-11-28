import customtkinter as ctk
import sys
import os
import threading
import webbrowser
import time
from PIL import Image

# --- CONFIGURATION ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class Launcher(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Setup
        self.title("PixelVault // Command Center")
        self.geometry("600x400")
        self.resizable(False, False)
        
        # --- LOGO SECTION ---
        # We try to load the logo, otherwise fallback to text
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "assets", "logo2.png")
        
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(40, 20))

        try:
            img_data = Image.open(logo_path)
            self.logo_image = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(60, 60))
            self.logo_lbl = ctk.CTkLabel(self.header_frame, text="", image=self.logo_image)
            self.logo_lbl.pack()
        except Exception:
            pass # No logo, no problem

        self.title_lbl = ctk.CTkLabel(self.header_frame, text="PIXELVAULT", 
                                      font=ctk.CTkFont(family="Roboto Medium", size=30, weight="bold"))
        self.title_lbl.pack(pady=5)

        self.subtitle_lbl = ctk.CTkLabel(self.header_frame, text="Select Operation Mode", 
                                         text_color="gray", font=ctk.CTkFont(size=14))
        self.subtitle_lbl.pack()

        # --- BUTTON SECTION ---
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=20)

        # Desktop Button
        self.btn_gui = ctk.CTkButton(self.btn_frame, text="DESKTOP APP", 
                                     font=ctk.CTkFont(size=16, weight="bold"),
                                     width=220, height=60, corner_radius=15,
                                     fg_color="#2b2b2b", hover_color="#3a3a3a", border_width=2, border_color="#10b981",
                                     command=self.launch_desktop)
        self.btn_gui.grid(row=0, column=0, padx=15)

        # Web Button
        self.btn_web = ctk.CTkButton(self.btn_frame, text="WEB SERVER", 
                                     font=ctk.CTkFont(size=16, weight="bold"),
                                     width=220, height=60, corner_radius=15,
                                     fg_color="#2b2b2b", hover_color="#3a3a3a", border_width=2, border_color="#3b82f6",
                                     command=self.launch_web_mode)
        self.btn_web.grid(row=0, column=1, padx=15)

        # --- STATUS SECTION ---
        self.status_lbl = ctk.CTkLabel(self, text="System Idle", text_color="gray")
        self.status_lbl.pack(side="bottom", pady=20)

    def launch_desktop(self):
        """Closes launcher and opens the Desktop App"""
        self.status_lbl.configure(text="Initializing Desktop Interface...", text_color="#10b981")
        self.update()
        time.sleep(0.5) # visuals
        
        self.destroy() # Close launcher
        
        # Import and run the GUI
        try:
            from gui.app import PixelVaultApp
            app = PixelVaultApp()
            app.mainloop()
        except ImportError as e:
            print(f"Error: {e}")

    def launch_web_mode(self):
        """Starts Flask in background and opens Browser"""
        self.status_lbl.configure(text="Starting Local Server...", text_color="#3b82f6")
        self.btn_web.configure(state="disabled", text="RUNNING...")
        self.btn_gui.configure(state="disabled")
        
        # 1. Start Flask in a separate thread
        server_thread = threading.Thread(target=self.run_flask, daemon=True)
        server_thread.start()

        # 2. Wait a moment for server to boot, then open browser
        self.after(1500, lambda: webbrowser.open("http://127.0.0.1:5000"))
        
        self.status_lbl.configure(text="Server Active at http://127.0.0.1:5000", text_color="#3b82f6")
        
        # Optional: Keep launcher open as a "Server Console" or minimize it
        # For now, we keep it open so the user can see the server is running.

    def run_flask(self):
        try:
            from web.app import app
            # Disable reloader to prevent main thread errors in this context
            app.run(port=5000, use_reloader=False) 
        except Exception as e:
            print(f"Server Error: {e}")

if __name__ == "__main__":
    # Check dependencies first
    try:
        import customtkinter
        import flask
        import stepic
        import PIL
    except ImportError as e:
        print("❌ Missing dependencies.")
        print(f"   Error: {e}")
        print("   Run: pip install -r requirements.txt")
        sys.exit(1)

    app = Launcher()
    app.mainloop()
