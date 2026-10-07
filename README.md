# 🖼️ Image Resizer (1920x1080)

A simple desktop GUI tool for batch image resizing built with **Python** and **Tkinter**.  
It automatically resizes all images in a selected folder to a maximum resolution of **1920×1080**, keeping aspect ratio and overwriting originals.

---

## 🚀 Features
- Resize all images in a folder (and subfolders) to fit 1920×1080  
- Preserve aspect ratio using high-quality **LANCZOS** filter  
- Skip already small images automatically  
- Live progress, ETA, and color-coded logs  
- Stop button for cancelling mid-process  
- Cross-platform (Windows, Linux, macOS)

---

## 🧰 Requirements

Python 3.8 or newer.

Install dependencies:

```bash
pip install -r requirements.txt
````

**requirements.txt**

```
Pillow>=10.0.0
```

---

## ▶️ Usage

1. Run the script:

   ```bash
   python image_resizer.py
   ```
2. Click **"Browse Folder & Start"**
3. Select the folder containing your images
4. The app will resize images and log results in real-time
5. You can stop processing anytime with the **Stop** button

---

## 📁 Supported Image Formats

* JPG / JPEG
* PNG
* BMP
* GIF
* TIFF
* WEBP

---

## 🧠 How It Works

* Scans all subfolders recursively
* Opens each image with Pillow
* Resizes if width > 1920 or height > 1080
* Saves resized image in place (overwrites)
* Updates GUI log and progress dynamically

---

## ⚠️ Notes

* The app **overwrites** original files.
  To preserve originals, copy your folder before resizing.
* If `tkinter` is missing, install it via your system package manager:

  * Ubuntu/Debian: `sudo apt install python3-tk`
  * Fedora: `sudo dnf install python3-tkinter`
  * macOS/Windows: included by default

---

## 🧑‍💻 Author

Developed by Vadim Darchuk
Feel free to fork, improve, or open issues on GitHub.

---

## 📜 License

MIT License

```

---
