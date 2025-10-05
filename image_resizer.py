import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
from PIL import Image

# Global variables
stop_flag = False
total_files = 0
processed_files = 0
resized_count = 0
skipped_count = 0
error_count = 0
start_time = 0
input_folder = ""
save_copies = tk.BooleanVar(value=True)
keep_aspect = tk.BooleanVar(value=True)  # toggle

# Default resolution
default_width = 1920
default_height = 1080

def get_target_resolution():
    try:
        w = int(width_entry.get())
        h = int(height_entry.get())
        return max(1, w), max(1, h)
    except ValueError:
        return default_width, default_height

def resize_image(path, log_widget, output_folder=None):
    global processed_files, resized_count, skipped_count, error_count
    max_w, max_h = get_target_resolution()
    aspect = keep_aspect.get()

    try:
        with Image.open(path) as img:
            img = img.convert("RGB")
            width, height = img.size

            # Output path
            if output_folder:
                rel_path = os.path.relpath(path, start=input_folder)
                save_path = os.path.join(output_folder, rel_path)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
            else:
                save_path = path

            # Only shrink, not enlarge
            if width > max_w or height > max_h:
                if aspect:
                    img.thumbnail((max_w, max_h), Image.LANCZOS)
                else:
                    img = img.resize((max_w, max_h), Image.LANCZOS)
                img.save(save_path, quality=95)
                resized_count += 1
                log_widget.insert(tk.END, f"Resized: {save_path}\n", "green")
            else:
                if save_path != path:  # copy if using copy mode
                    img.save(save_path, quality=95)
                skipped_count += 1
                log_widget.insert(tk.END, f"Skipped: {path}\n", "gray")

    except Exception as e:
        error_count += 1
        log_widget.insert(tk.END, f"Error processing {path}: {e}\n", "red")

    processed_files += 1
    update_status()
    log_widget.see(tk.END)
    log_widget.update_idletasks()

def resize_images_in_folder(root_folder, log_widget):
    global stop_flag, total_files, processed_files, start_time
    global resized_count, skipped_count, error_count, input_folder

    input_folder = root_folder
    resized_count = skipped_count = error_count = processed_files = 0
    log_widget.insert(tk.END, "Scanning folder...\n", "gray")
    log_widget.update_idletasks()

    # Collect image paths
    image_paths = []
    for dirpath, _, filenames in os.walk(root_folder):
        for file in filenames:
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp")):
                image_paths.append(os.path.join(dirpath, file))

    total_files = len(image_paths)
    start_time = time.time()

    if total_files == 0:
        log_widget.insert(tk.END, "No images found.\n", "red")
        stop_button.config(state=tk.DISABLED)
        return

    # Prepare output folder if needed
    output_folder = None
    if save_copies.get():
        max_w, max_h = get_target_resolution()
        output_folder = os.path.join(root_folder, f"Resized_{max_w}x{max_h}")
        os.makedirs(output_folder, exist_ok=True)

    for full_path in image_paths:
        if stop_flag:
            log_widget.insert(tk.END, "\n--- Stopped by user ---\n", "red")
            log_widget.see(tk.END)
            stop_button.config(state=tk.DISABLED)
            show_summary_popup()
            return
        resize_image(full_path, log_widget, output_folder)

    status_label.config(text=f"Done! Processed {processed_files}/{total_files} images.")
    progress_bar["value"] = 100
    stop_button.config(state=tk.DISABLED)
    show_summary_popup()

def start_resizing(folder, log_widget):
    global stop_flag
    stop_flag = False
    log_widget.delete(1.0, tk.END)
    log_widget.insert(tk.END, f"Opened folder: {folder}\n\n", "gray")
    log_widget.update_idletasks()
    stop_button.config(state=tk.NORMAL)

    thread = threading.Thread(target=resize_images_in_folder, args=(folder, log_widget))
    thread.start()

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        start_resizing(folder, log_widget)

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
    progress_bar["value"] = percent
    progress_bar.update_idletasks()
    status_label.update_idletasks()

def show_summary_popup():
    elapsed = time.time() - start_time
    mins, secs = divmod(int(elapsed), 60)
    messagebox.showinfo(
        "Summary",
        f"✅ Resizing complete\n\n"
        f"Total images: {total_files}\n"
        f"Resized: {resized_count}\n"
        f"Skipped: {skipped_count}\n"
        f"Errors: {error_count}\n\n"
        f"Elapsed time: {mins:02d}:{secs:02d}"
    )

# GUI setup
root = tk.Tk()
root.title("Image Resizer (Custom Resolution + Summary)")
root.geometry("900x780")

log_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="black", fg="white", height=25)
log_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
log_widget.tag_config("green", foreground="lime")
log_widget.tag_config("gray", foreground="gray")
log_widget.tag_config("red", foreground="red")

progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
progress_bar.pack(fill=tk.X, padx=10, pady=5)

# Resolution and aspect ratio controls
options_frame = tk.Frame(root)
options_frame.pack(pady=5)
tk.Label(options_frame, text="Width:").pack(side=tk.LEFT, padx=3)
width_entry = tk.Entry(options_frame, width=6)
width_entry.insert(0, str(default_width))
width_entry.pack(side=tk.LEFT)
tk.Label(options_frame, text="Height:").pack(side=tk.LEFT, padx=3)
height_entry = tk.Entry(options_frame, width=6)
height_entry.insert(0, str(default_height))
height_entry.pack(side=tk.LEFT)
keep_aspect_checkbox = tk.Checkbutton(options_frame, text="Keep aspect ratio", variable=keep_aspect)
keep_aspect_checkbox.pack(side=tk.LEFT, padx=10)

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)
browse_button = tk.Button(btn_frame, text="Browse Folder & Start", command=browse_folder)
browse_button.pack(side=tk.LEFT, padx=5)
stop_button = tk.Button(btn_frame, text="Stop", command=stop_resizing, fg="red", state=tk.DISABLED)
stop_button.pack(side=tk.LEFT, padx=5)

# Save copies checkbox
copy_checkbox = tk.Checkbutton(root, text="Save copies to new folder", variable=save_copies)
copy_checkbox.pack(pady=5)

status_label = tk.Label(root, text="Idle", anchor="w")
status_label.pack(fill=tk.X, pady=5)

root.mainloop()
