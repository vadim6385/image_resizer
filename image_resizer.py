import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from PIL import Image


class ImageResizerApp:
    """Build and run the Tkinter interface for batch image resizing."""

    DEFAULT_WIDTH = 1920
    DEFAULT_HEIGHT = 1080
    SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp")

    def __init__(self):
        """Create the application window, initialize state, and build its controls."""
        self.root = tk.Tk()
        self.root.title("Image Resizer (Custom Resolution + Summary)")
        self.root.geometry("900x780")

        self.save_copies = tk.BooleanVar(master=self.root, value=True)
        self.keep_aspect = tk.BooleanVar(master=self.root, value=True)
        self.stop_requested = False
        self.total_files = 0
        self.processed_files = 0
        self.resized_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.start_time = 0.0
        self.input_folder = ""

        self._build_ui()

    def _build_ui(self):
        """Create and lay out the log, progress bar, options, and action buttons."""
        self.log_widget = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, bg="black", fg="white", height=25
        )
        self.log_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.log_widget.tag_config("green", foreground="lime")
        self.log_widget.tag_config("gray", foreground="gray")
        self.log_widget.tag_config("red", foreground="red")

        self.progress_bar = ttk.Progressbar(
            self.root, orient="horizontal", mode="determinate"
        )
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

        options_frame = tk.Frame(self.root)
        options_frame.pack(pady=5)
        tk.Label(options_frame, text="Width:").pack(side=tk.LEFT, padx=3)
        self.width_entry = tk.Entry(options_frame, width=6)
        self.width_entry.insert(0, str(self.DEFAULT_WIDTH))
        self.width_entry.pack(side=tk.LEFT)
        tk.Label(options_frame, text="Height:").pack(side=tk.LEFT, padx=3)
        self.height_entry = tk.Entry(options_frame, width=6)
        self.height_entry.insert(0, str(self.DEFAULT_HEIGHT))
        self.height_entry.pack(side=tk.LEFT)
        tk.Checkbutton(
            options_frame,
            text="Keep aspect ratio",
            variable=self.keep_aspect,
        ).pack(side=tk.LEFT, padx=10)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        tk.Button(
            button_frame,
            text="Browse Folder & Start",
            command=self.browse_folder,
        ).pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(
            button_frame,
            text="Stop",
            command=self.stop_resizing,
            fg="red",
            state=tk.DISABLED,
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        tk.Checkbutton(
            self.root,
            text="Save copies to new folder",
            variable=self.save_copies,
        ).pack(pady=5)

        self.status_label = tk.Label(self.root, text="Idle", anchor="w")
        self.status_label.pack(fill=tk.X, pady=5)

    def run(self):
        """Start Tkinter's event loop and display the application window."""
        self.root.mainloop()

    def get_target_resolution(self):
        """Read the requested dimensions, falling back to defaults for invalid input."""
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            return max(1, width), max(1, height)
        except ValueError:
            return self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT

    def resize_image(self, path, output_folder=None):
        """Resize one image when needed, save it, and update processing counters."""
        max_width, max_height = self.get_target_resolution()
        keep_aspect = self.keep_aspect.get()

        try:
            with Image.open(path) as image:
                image = image.convert("RGB")
                width, height = image.size

                if output_folder:
                    relative_path = os.path.relpath(path, start=self.input_folder)
                    save_path = os.path.join(output_folder, relative_path)
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                else:
                    save_path = path

                if width > max_width or height > max_height:
                    if keep_aspect:
                        image.thumbnail((max_width, max_height), Image.LANCZOS)
                    else:
                        image = image.resize(
                            (max_width, max_height), Image.LANCZOS
                        )
                    image.save(save_path, quality=95)
                    self.resized_count += 1
                    self.log_widget.insert(
                        tk.END, f"Resized: {save_path}\n", "green"
                    )
                else:
                    if save_path != path:
                        image.save(save_path, quality=95)
                    self.skipped_count += 1
                    self.log_widget.insert(tk.END, f"Skipped: {path}\n", "gray")

        except Exception as error:
            self.error_count += 1
            self.log_widget.insert(
                tk.END, f"Error processing {path}: {error}\n", "red"
            )

        self.processed_files += 1
        self.update_status()
        self.log_widget.see(tk.END)
        self.log_widget.update_idletasks()

    def resize_images_in_folder(self, root_folder):
        """Find supported images in a folder and process them until complete or stopped."""
        self.input_folder = root_folder
        self.resized_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.processed_files = 0
        self.log_widget.insert(tk.END, "Scanning folder...\n", "gray")
        self.log_widget.update_idletasks()

        image_paths = []
        for directory, _, filenames in os.walk(root_folder):
            for filename in filenames:
                if filename.lower().endswith(self.SUPPORTED_EXTENSIONS):
                    image_paths.append(os.path.join(directory, filename))

        self.total_files = len(image_paths)
        self.start_time = time.time()

        if self.total_files == 0:
            self.log_widget.insert(tk.END, "No images found.\n", "red")
            self.stop_button.config(state=tk.DISABLED)
            return

        output_folder = None
        if self.save_copies.get():
            max_width, max_height = self.get_target_resolution()
            output_folder = os.path.join(
                root_folder, f"Resized_{max_width}x{max_height}"
            )
            os.makedirs(output_folder, exist_ok=True)

        for image_path in image_paths:
            if self.stop_requested:
                self.log_widget.insert(
                    tk.END, "\n--- Stopped by user ---\n", "red"
                )
                self.log_widget.see(tk.END)
                self.stop_button.config(state=tk.DISABLED)
                self.show_summary_popup()
                return
            self.resize_image(image_path, output_folder)

        self.status_label.config(
            text=f"Done! Processed {self.processed_files}/{self.total_files} images."
        )
        self.progress_bar["value"] = 100
        self.stop_button.config(state=tk.DISABLED)
        self.show_summary_popup()

    def start_resizing(self, folder):
        """Reset the log and start processing the selected folder on a worker thread."""
        self.stop_requested = False
        self.log_widget.delete(1.0, tk.END)
        self.log_widget.insert(tk.END, f"Opened folder: {folder}\n\n", "gray")
        self.log_widget.update_idletasks()
        self.stop_button.config(state=tk.NORMAL)

        thread = threading.Thread(
            target=self.resize_images_in_folder, args=(folder,)
        )
        thread.start()

    def browse_folder(self):
        """Ask the user to select a folder, then begin resizing its images."""
        folder = filedialog.askdirectory()
        if folder:
            self.start_resizing(folder)

    def stop_resizing(self):
        """Request that the active folder-processing loop stop."""
        self.stop_requested = True

    def update_status(self):
        """Refresh the progress bar, processed-image count, and estimated time remaining."""
        if self.total_files == 0:
            return

        percent = (self.processed_files / self.total_files) * 100
        elapsed = time.time() - self.start_time
        average_time = elapsed / self.processed_files if self.processed_files else 0
        remaining = (self.total_files - self.processed_files) * average_time
        eta = time.strftime("%M:%S", time.gmtime(remaining))
        self.status_label.config(
            text=(
                f"Processed {self.processed_files}/{self.total_files} "
                f"({percent:.1f}%) | ETA: {eta}"
            )
        )
        self.progress_bar["value"] = percent
        self.progress_bar.update_idletasks()
        self.status_label.update_idletasks()

    def show_summary_popup(self):
        """Display a summary of the image counts and elapsed processing time."""
        elapsed = time.time() - self.start_time
        minutes, seconds = divmod(int(elapsed), 60)
        messagebox.showinfo(
            "Summary",
            f"✅ Resizing complete\n\n"
            f"Total images: {self.total_files}\n"
            f"Resized: {self.resized_count}\n"
            f"Skipped: {self.skipped_count}\n"
            f"Errors: {self.error_count}\n\n"
            f"Elapsed time: {minutes:02d}:{seconds:02d}",
        )


if __name__ == "__main__":
    # Create and run the GUI only when this file is executed directly.
    ImageResizerApp().run()
