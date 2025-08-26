import tkinter
from tkinter import filedialog, messagebox
import threading
import os
import sys
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD

CHUNK_SIZE = 6536
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class CryptoApp:
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title("CryptFile: Encrypt and Decrypt your Files")
        self.root.geometry("900x600")
        self.root.configure(bg="#1a1a1a")
        self.file_path = None
        self.is_processing = False
        self.root.iconbitmap("lock.ico")
        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.sidebar_label = ctk.CTkLabel(
            self.sidebar, text="CryptFile", font=("Arial", 20, "bold")
        )
        self.sidebar_label.pack(pady=20)
         # --- Vertical separation line ---
        self.separator = ctk.CTkFrame(self.root, width=1,fg_color="black") 
        self.separator.pack(side="left", fill="y")  
        self.button_home = ctk.CTkButton(
            self.sidebar, text="🏠 Home", command=self.show_home, anchor="w"
        )
        self.button_home.pack(fill="x", pady=5, padx=10)

        self.button_encrypt = ctk.CTkButton(
            self.sidebar, text="🔒 Encryption", command=self.show_encrypt_tab, anchor="w"
        )
        self.button_encrypt.pack(fill="x", pady=5, padx=10)

        self.button_decrypt = ctk.CTkButton(
            self.sidebar, text="🔓 Decryption", command=self.show_decrypt_tab, anchor="w"
        )
        self.button_decrypt.pack(fill="x", pady=5, padx=10)
        # --- Footer ---
        self.footer = ctk.CTkFrame(self.root, height=30, corner_radius=0)
        self.footer.pack(side="bottom", fill="x")  

        self.footer_label = ctk.CTkLabel(
            self.footer,
            text="CryptFile v1.8  |  Developped by ttl77998. ",
            font=("Arial", 12),
            text_color="gray"
        )
                # --- Main Zone ---
        self.footer_label.pack(expand=True)  # Horizontal and vertical centring
        self.main_area = ctk.CTkFrame(self.root)
        self.main_area.pack(side="right", expand=True, fill="both")

        self.show_home()

    # --- Home  ---
    def show_home(self):
        self.clear_main_area()
        home_label = ctk.CTkLabel(
            self.main_area,
            text="Welcome to CryptFile\nSelect an option in the side bar",
            font=("Arial", 24, "bold"),
        )
        home_label.pack(expand=True)    # Horizontal and vertical centring

    # --- Encryption ---
    def show_encrypt_tab(self):
        self.clear_main_area()
        self.build_tab(mode="encrypt")

    # --- Decryption ---
    def show_decrypt_tab(self):
        self.clear_main_area()
        self.build_tab(mode="decrypt")

    # --- Construct Encryption/Decryption ---
    def build_tab(self, mode):
        label_password = ctk.CTkLabel(
            self.main_area, text="Password:", font=("Arial", 16)
        )
        label_password.pack(pady=(10, 0))

        self.entry_password = ctk.CTkEntry(self.main_area, width=300, show="*")
        self.entry_password.pack(pady=(0, 10))

        select_button = ctk.CTkButton(
            self.main_area,
            text="Select a file",
            command=lambda: self.select_file(mode),
        )
        select_button.pack(pady=10)

        # File zone 
        self.file_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.file_frame.pack(pady=(10, 0))

        self.label_file_icon = ctk.CTkLabel(
            self.file_frame, text="📄", font=("Arial", 20)
        )
        self.label_file_icon.pack(side="left", padx=5)

        self.label_file_name = ctk.CTkLabel(
            self.file_frame, text="No file selected", font=("Arial", 16)
        )
        self.label_file_name.pack(side="left", padx=5)

        self.label_file_path = ctk.CTkLabel(
            self.main_area,
            text="(or drag and drop it here)",
            font=("Arial", 12),
            text_color="gray",
        )
        self.label_file_path.pack(pady=(0, 20))

        # Drag & drop
        self.label_file_path.drop_target_register(DND_FILES)
        self.label_file_path.dnd_bind("<<Drop>>", lambda e: self.on_drop(e, mode))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.main_area, width=300)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(0, 10))

        self.label_status = ctk.CTkLabel(self.main_area, text="", font=("Arial", 12))
        self.label_status.pack(pady=(0, 20))

        # Action buttons
        if mode == "encrypt":
            button_action = ctk.CTkButton(
                self.main_area,
                text="Encrypt",
                command=self.start_encrypt,
                fg_color="green",
                hover_color="#216a30",
            )
        else:
            button_action = ctk.CTkButton(
                self.main_area,
                text="Decrypt",
                command=self.start_decrypt,
                fg_color="red",
                hover_color="#8a1818",
            )
        button_action.pack(pady=5)
       
    # --- Clear the main zone ---
    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    # --- File selection ---
    def select_file(self, mode):
        if self.is_processing:
            return
        file_path = filedialog.askopenfilename()
        if file_path:
            if mode == "decrypt" and not file_path.endswith(".enc"):
                messagebox.showwarning("Error", "The file must be with the extension '.enc'")
                return
            self.file_path = file_path
            self._update_file_labels(file_path)

    # --- Drag & Drop ---
    def on_drop(self, event, mode):
        if self.is_processing:
            return
        file_path_raw = event.data
        if file_path_raw.startswith("{") and file_path_raw.endswith("}"):
            file_path_clean = file_path_raw[1:-1]
        else:
            file_path_clean = file_path_raw

        if not os.path.isfile(file_path_clean):
            messagebox.showwarning("Error", "Drag and drop a valid file")
            return

        if mode == "decrypt" and not file_path_clean.endswith(".enc"):
            messagebox.showwarning("Error", "The file must be with the extension '.enc'")
            return

        self.file_path = file_path_clean
        self._update_file_labels(file_path_clean)

    # --- File Label MAJ ---
    def _update_file_labels(self, path):
        self.label_file_name.configure(text=os.path.basename(path), text_color="white")
        self.label_file_path.configure(text=path, text_color="gray")
        self.label_file_icon.configure(text="🔒" if path.endswith(".enc") else "📄")

    # --- Key generating ---
    def _generate_key(self, password):
        password_bytes = password.encode()
        salt = b"uhsfiuhiuhfgiusdfuigfiughiufhidughudfhuighfd"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        return base64.urlsafe_b64encode(kdf.derive(password_bytes))

    # --- Main actions ---
    def start_encrypt(self):
        if self.is_processing:
            return
        self.is_processing = True
        self.label_status.configure(text="Encryption in process...")
        threading.Thread(target=self.encrypt_file).start()

    def start_decrypt(self):
        if self.is_processing:
            return
        self.is_processing = True
        self.label_status.configure(text="Decryption in process...")
        threading.Thread(target=self.decrypt_file).start()

    def encrypt_file(self):
        if not self.file_path:
            messagebox.showwarning("Error", "No file selected !")
            self.is_processing = False
            return
        password = self.entry_password.get()
        if not password:
            messagebox.showwarning("Error", "The password is required !")
            self.is_processing = False
            return

        try:
            key = self._generate_key(password)
            f = Fernet(key)

            file_size = os.path.getsize(self.file_path)
            bytes_read = 0
            encrypted_file_path = self.file_path + ".enc"

            with open(self.file_path, "rb") as infile, open(
                encrypted_file_path, "wb"
            ) as outfile:
                while True:
                    chunk = infile.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    encrypted_chunk = f.encrypt(chunk)
                    outfile.write(encrypted_chunk)
                    bytes_read += len(chunk)
                    self.progress_bar.set(bytes_read / file_size)
                    self.root.update_idletasks()

            messagebox.showinfo("Success", f"Crypted file: {encrypted_file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.reset_after_action()

    def decrypt_file(self):
        if not self.file_path:
            messagebox.showwarning("Error", "No file selected")
            self.is_processing = False
            return
        password = self.entry_password.get()
        if not password:
            messagebox.showwarning("Error", " The password is required !")
            self.is_processing = False
            return

        try:
            key = self._generate_key(password)
            f = Fernet(key)

            file_size = os.path.getsize(self.file_path)
            bytes_read = 0
            decrypted_file_path = self.file_path.removesuffix(".enc")

            with open(self.file_path, "rb") as infile, open(
                decrypted_file_path, "wb"
            ) as outfile:
                while True:
                    chunk = infile.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    decrypted_chunk = f.decrypt(chunk)
                    outfile.write(decrypted_chunk)
                    bytes_read += len(chunk)
                    self.progress_bar.set(bytes_read / file_size)
                    self.root.update_idletasks()

            messagebox.showinfo("Success", f"Decrypted file: {decrypted_file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Decryption error: {e}")
        finally:
            self.reset_after_action()

    def reset_after_action(self):
        self.file_path = None
        self.label_file_name.configure(text="No file selected")
        self.label_file_path.configure(text="(or drag and drop it here)")
        self.label_file_icon.configure(text="📄")
        self.progress_bar.set(0)
        self.label_status.configure(text="Finish !")
        self.is_processing = False


def show_splash_screen():
    splash = tkinter.Tk()
    splash.overrideredirect(True)
    splash.geometry("850x200+480+300")
    splash.configure(bg="#1a1a1a")
    splash.attributes("-alpha", 0.0)

    label = tkinter.Label(
        splash, text="CryptFile", font=("Segoe UI", 26, "bold"), fg="white", bg="#1a1a1a"
    )
    label.pack(expand=True)

    def fade_in(alpha):
        alpha = round(alpha + 0.05, 2)
        if alpha <= 1.0:
            splash.attributes("-alpha", alpha)
            splash.after(50, fade_in, alpha)
        else:
            splash.after(1500, splash.destroy)

    splash.after(0, fade_in, 0.0)
    splash.mainloop()

def resource_path(relative_path):
    """Return the absolute path of all the files to PyInstaller."""
    try:
        # PyInstaller create a temp _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    show_splash_screen()
    app = CryptoApp()
    app.root.mainloop()

