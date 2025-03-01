import subprocess
import sys

# moduler
required_modules = ['art', 'tkinter', 're', 'os', 'time', 'random', 'subprocess']

def install_module(module_name):
    """Install a missing module using pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])

def check_and_install_modules():
    """Check and install any missing modules."""
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            print(f"Module {module} is missing. Installing...")
            install_module(module)

# installera-moduler
check_and_install_modules()

# programmet
import art
import os
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
import random
import time
import re

def display_ascii_art():
    ascii_banner = art.text2art("MX NetTool", font="small")
    print(ascii_banner)

def hide_console():
    if os.name == "nt":
        display_ascii_art()
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def modify_ping_response(line):
    if "time=" in line and random.randint(1, 5) == 1:  # hög-latens
        fake_latency = random.randint(500, 9000)  # hög-ping
        time.sleep(fake_latency / 1000)  # pausa
        line = re.sub(r"time=\d+ms", f"time={fake_latency}ms", line)
    
    # styrka
    line = re.sub(r"bytes=(\d+)", r"strength=\1", line)
    return line

current_process = None

def ping(ip, size, output_text):
    global current_process
    
    if size > 65500:
        messagebox.showerror("Error", "Size exceeds max allowed (65500 bytes).")
        return

    if current_process:
        current_process.terminate()
    
    command = ["ping", ip, "-t", "-l", str(size)] if os.name == "nt" else ["ping", ip, "-s", str(size)]
    
    if os.name != "nt":
        command += ["-M", "do"]

    try:
        current_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        while current_process.poll() is None:
            line = current_process.stdout.readline()
            if not line:
                continue

            # latens koll
            line = modify_ping_response(line)
            output_text.insert(tk.END, f"> {line}")
            output_text.see(tk.END)

    except Exception as e:
        messagebox.showerror("Error", f"Ping failed: {e}")

def start_ping():
    ip = ip_entry.get()
    try:
        size = int(size_entry.get())
        if size < 1 or size > 65500:
            raise ValueError("Packet size must be 1-65500 bytes.")
    except ValueError:
        messagebox.showerror("Error", "Invalid packet size. Enter a number between 1-65500.")
        return
    
    output_text.delete(1.0, tk.END)
    thread = threading.Thread(target=ping, args=(ip, size, output_text), daemon=True)
    thread.start()

def exit_app():
    global current_process
    if current_process:
        current_process.terminate()
    root.quit()

hide_console()

root = tk.Tk()
root.title("MX NetTool")
root.geometry("600x400")
root.configure(bg="black")

# namn
title_label = tk.Label(root, text="MX NetTool", font=("Courier", 20, "bold"), fg="green", bg="black")
title_label.pack()

# inputs
tk.Label(root, text="Ip Address:", fg="green", bg="black", font=("Courier", 12)).pack()
ip_entry = tk.Entry(root, bg="black", fg="green", insertbackground="green", font=("Courier", 12))
ip_entry.pack()

tk.Label(root, text="Strength:", fg="green", bg="black", font=("Courier", 12)).pack()
size_entry = tk.Entry(root, bg="black", fg="green", insertbackground="green", font=("Courier", 12))
size_entry.pack()

# modul gui
button_frame = tk.Frame(root, bg="black")
button_frame.pack(pady=10)

button_style = {"fg": "black", "bg": "green", "font": ("Courier", 12, "bold"), "padx": 10, "pady": 5}

tk.Button(button_frame, text="Start", command=start_ping, **button_style).pack(side="left", padx=5)
tk.Button(button_frame, text="Exit", command=exit_app, **button_style).pack(side="left", padx=5)

# output-terminalen
output_text = scrolledtext.ScrolledText(root, height=10, bg="black", fg="green", font=("Courier", 10), insertbackground="green")
output_text.pack()

root.mainloop()
