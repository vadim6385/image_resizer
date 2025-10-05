import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, scrolledtext
from PIL import Image

MAX_WIDTH = 1920
MAX_HEIGHT = 1080

# Global flags
stop_flag = False
total_files = 0
processed_files = 0
start_time = 0

def resize_image(path, log_widget):
    global processed_files
    try:
        with Image.open(path) as img:
            img = img.copy()  # ignore EXIF orientation
            width, height = img.size

            if width > MAX_WIDTH or height > MAX_HEIGHT:
                img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.LANCZOS)
                img.save(path)
                log_widget.insert(tk.END, f"Resized: {path}\n", "green")
            else:
                log_widget.insert(tk.END, f"Skipped: {path}\n", "gray")
    except Exception as e:
        log_widget.insert(tk.END, f"Error processing {path}: {e}\n", "red")

    processed_files += 1
    update_status()
    log_widget.see(tk.END)
    log_widget.update_idletasks()

def resize_images_in_folder(root_folder, log_widget):
    global stop_flag, total_files, processed_files, start_time
    # Collect all files first for progress tracking
    image_paths = []
    for dirpath, _, filenames in os.walk(root_folder):
        for file in filenames:
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp")):
                image_paths.append(os.path.join(dirpath, file))

    total_files = len(image_paths)
    processed_files = 0
    start_time = time.time()

    for full_path in image_paths:
        if stop_flag:  
            log_widget.insert(tk.END, "\n--- Stopped by user ---\n", "red")
            log_widget.see(tk.END)
            return
        resize_image(full_path, log_widget)

    status_label.config(text=f"Done! Processed {processed_files}/{total_files} images.")
    stop_button.config(state=tk.DISABLED)

def start_resizing(folder, log_widget):
    global stop_flag
    stop_flag = False
    log_widget.delete(1.0, tk.END)
    log_widget.insert(tk.END, f"Selected folder: {folder}\n\n", "gray")
    log_widget.update_idletasks()
    stop_button.config(state=tk.NORMAL)
    resize_images_in_folder(folder, log_widget)

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        thread = threading.Thread(target=start_resizing, args=(folder, log_widget))
        thread.start()

def stop_resizing():
    global stop_flag
    stop_flag = True

def update_status():
    if total_files == 0:
        return
    percent = (processed_files / total_files) * 100
    elapsed = time.time() - start_time
    avg_time = elapsed / processed_files if processed_files > 0 else 0
    remaining = (total_files - processed_files) * avg_time
    eta = time.strftime("%M:%S", time.gmtime(remaining))
    status_label.config(
        text=f"Processed {processed_files}/{total_files} ({percent:.1f}%) | ETA: {eta}"
    )
    status_label.update_idletasks()

# GUI setup
root = tk.Tk()
root.title("Image Resizer (1920x1080)")
root.geometry("900x650")

log_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="black", fg="white")
log_widget.pack(fill=tk.BOTH, expand=True)

log_widget.tag_config("green", foreground="lime")
log_widget.tag_config("gray", foreground="gray")
log_widget.tag_config("red", foreground="red")

frame = tk.Frame(root)
frame.pack(pady=10)

browse_button = tk.Button(frame, text="Browse Folder & Start", command=browse_folder)
browse_button.pack(side=tk.LEFT, padx=5)

stop_button = tk.Button(frame, text="Stop", command=stop_resizing, fg="red", state=tk.DISABLED)
stop_button.pack(side=tk.LEFT, padx=5)

status_label = tk.Label(root, text="Idle", anchor="w")
status_label.pack(fill=tk.X, pady=5)

root.mainloop()
