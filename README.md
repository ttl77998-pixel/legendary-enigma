# 🔐 CryptFile

**CryptFile** is a Python desktop application for securely **encrypting** and **decrypting** files using a password.  
It features a sleek dark-mode UI, drag-and-drop support, and real-time progress tracking.

---

## ✨ Features

- **File Encryption & Decryption** with Fernet symmetric encryption
- **Password-Based Key Generation** (PBKDF2HMAC)
- **Dark UI** built with `customtkinter`
- **Drag & Drop** for quick file selection
- **Progress Bar** for operation status
- **Splash Screen** at startup
- **File Type Validation** (`.enc` required for decryption)

---

## 📦 Requirements

Before running or building the app, install the dependencies:

```bash
pip install cryptography customtkinter tkinterdnd2
```
When you have install all the dependencies, build the app with the following command
```bash
pyinstaller cryptApp.spec
```
After building the app, add `lock.ico` and `lock.png` in the CrypFile folder that will be create

---

## 🧑‍💻 Author 
- **Developed by**: UnknowCoder
-  **Version**: 1.8
