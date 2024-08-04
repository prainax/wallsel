#!/bin/python3
import tkinter as tk
from tkinter import ttk
from sys import argv
from os import environ, path, listdir
from datetime import datetime
from PIL import Image, ImageTk
import threading

HOME = environ.get("HOME")
DEFAULT_DIR = f"{HOME}/Pictures/"
FONT = ("monospace", 9)

class WallGUI:
    def __init__(self, dir_path: str = DEFAULT_DIR) -> None:
        self.window_color()
        self.dir_path = dir_path
        self.thumbnail_size = (128, 128)

        self.root = tk.Tk()
        self.root.title("wallsel")


        self.configure_window()
        self.show_images()
        self.bar()

        self.root.mainloop()

    def configure_window(self):
        window_width = 800
        window_height = 600

        # get the screen dimension
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # find the center point
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        # set the position of the window to the center of the screen
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    def window_color(self):
        # get colors from Xresources for windows background
        from subprocess import run as sub_run

        filepath = f"{HOME}/.Xresources"

        try:
            output = sub_run(
                ['grep', '-i', '-e', r'\*\.background', '-e', r'\*\.foreground', filepath],
                capture_output=True
            )

            out_list = output.stdout.strip().decode("utf-8").split()

            self.fg = out_list[1]
            self.bg = out_list[3]
        except Exception as e:
            print(f"[ERROR] Failed to get colors from .Xresources: {e}")
            self.bg = '#ffffff'  # default background color
            self.fg = '#000000'  # default foreground color

    def bar(self):
        # Create a frame for the bottom bar
        bar = tk.Frame(self.root, bg=self.fg, height=30)
        bar.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)

        # Add widgets to the bottom bar
        status_label = tk.Label(bar, text="Status: Ready", bg=self.bg)
        status_label.pack(side=tk.LEFT, padx=10)

        date_and_time = f"{datetime.now().strftime('%a, %e %B')} {datetime.now().strftime('%I:%M:%S %p')}"

        date_and_time_label = tk.Label(bar, text=date_and_time, bg=self.fg, fg=self.bg, font=FONT)
        date_and_time_label.pack(side=tk.RIGHT, padx=1)

    def calculate_images_per_row(self):
        # Get the width of the window
        window_width = self.root.winfo_width()

        # Image width including padding
        image_width = self.thumbnail_size[0] + 10  # Adding padding

        # Calculate the number of images that fit in one row
        num_images_per_row = max(1, window_width // image_width)

        return num_images_per_row

    def on_window_resize(self, event):
        # Recalculate and update the grid layout when the window is resized
        num_images_per_row = self.calculate_images_per_row()
        self.update_image_grid(num_images_per_row)

    def update_image_grid(self, num_images_per_row):
        # Recreate the layout based on the new number of images per row
        for widget in self.thumbnail_frame.winfo_children():
            widget.destroy()

        for i, img_tk in enumerate(self.thumbnails):
            row = i // num_images_per_row
            col = i % num_images_per_row

            label = ttk.Label(self.thumbnail_frame, image=img_tk)
            label.image = img_tk
            label.grid(row=row, column=col, padx=5, pady=5)

    def list_images(self):
        self.images_per_row = 6

        # List of common image file extensions
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}

        try:
            # List all entries in the directory
            entries = listdir(self.dir_path)

            # Filter out files with image extensions
            image_files = [
                entry for entry in entries
                if path.isfile(path.join(self.dir_path, entry)) and
                path.splitext(entry)[1].lower() in image_extensions
            ]

            return image_files

        except Exception as e:
            print(f"[ERROR] Failed to list images: {e}")
            return []

    def load_images(self):
        valid_images = []
        for image in self.list_images():
            image_path = path.join(self.dir_path, image)

            try:
                with Image.open(image_path) as img:
                    img.verify()  # Verify the image without loading it into memory
                valid_images.append(image)
            except Exception as e:
                print(f"[ERROR] unable to load image: {image_path}, {e}")

        self.thumbnails = []
        for i, image in enumerate(valid_images):
            image_path = path.join(self.dir_path, image)

            with Image.open(image_path) as img:
                img.thumbnail(self.thumbnail_size)
                thumbnail = ImageTk.PhotoImage(img)
                self.thumbnails.append(thumbnail)

            self.root.after(0, self.display_image, thumbnail, i)

    def display_image(self, img_tk, index):
        # Calculate the number of images per row based on window width
        num_images_per_row = self.calculate_images_per_row()

        # Calculate row and column for the image
        row = index // num_images_per_row
        col = index % num_images_per_row

        # Create a label to display the image
        label = ttk.Label(self.thumbnail_frame, image=img_tk)
        label.image = img_tk  # Keep a reference to avoid garbage collection
        label.grid(row=row, column=col, padx=5, pady=5)

    def show_images(self):
        images = self.list_images()
        self.thumbnails = []

        # Create a frame for the thumbnails
        self.thumbnail_frame = ttk.Frame(self.root)
        self.thumbnail_frame.pack(fill=tk.BOTH, expand=True)

        # Start loading images in a separate thread
        self.load_images_thread = threading.Thread(target=self.load_images)
        self.load_images_thread.start()

        if len(images) == 0:
            print("[ERROR] no image found")
            exit(1)

# main function
def main():
    if len(argv) > 1 and path.isdir(argv[1]):
        dir_path = argv[1]
    else:
        print(f"[INFO] Using default directory: {DEFAULT_DIR}")
        dir_path = DEFAULT_DIR

    try:
        gui = WallGUI(dir_path)
    except Exception as e:
        print(f"[ERROR] Failed to initialize GUI: {e}")
        exit(1)

if __name__ == "__main__":
    main()
