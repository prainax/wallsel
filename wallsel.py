#!/bin/python3
import tkinter as tk
from tkinter import font
from sys import argv
from os import environ, path, listdir
from datetime import datetime
from PIL import Image, ImageTk



HOME = environ.get("HOME")
DEFAULT_DIR = f"{HOME}/Pictures/"
FONT=("monospace", 9)



class WallGUI:
    def __init__(self, dir_path: str = DEFAULT_DIR) -> None:
        self.window_color()
        self.dir_path = dir_path
        

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
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)

# set the position of the window to the center of the screen
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')


    def window_color(self):
        # get colors from Xresources for windows background 
        from subprocess import run as sub_run

        filepath = f"{HOME}/.Xresources"

        try:
            output = sub_run(
                     ['grep', '-i',  '-e', r'\*\.background', '-e', r'\*\.foreground', filepath],
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

        date_and_time = f"{datetime.now().strftime("%a,%e %B")} {datetime.now().strftime("%I:%M:%S %p")}"

        date_and_time_label = tk.Label(bar, text=date_and_time, bg=self.fg, fg=self.bg, font=FONT)
        date_and_time_label.pack(side=tk.RIGHT, padx=1)



    def list_images(self):
        #print(self.dir_path)

# List of common image file extensions
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', }
        
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

        except:
            return []

    def show_images(self):

        images = self.list_images()
        thumbnail = None

        if len(images) == 0:
            print("[ERROR] no image found")
            exit(1)


        for image in images:
            image_path = path.join(self.dir_path, image)
            with Image.open(image_path) as img:
                img.thumbnail((80,80))
                thumbnail = ImageTk.PhotoImage(img)

            print(f"{image} {image_path} {thumbnail}".split())
        frame = tk.Frame(self.root, bg=self.bg)
        frame.pack(padx=10, pady=10)

        # Create a label for each image thumbnail
        label = tk.Label(frame, image=thumbnail, compound=tk.TOP)
        label.pack(side=tk.LEFT, padx=5, pady=5)

        # Keep a reference to avoid garbage collection
        label.image = thumbnail








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
