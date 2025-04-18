import tkinter as tk
import subprocess
import os

def run_ade():
    script_path = os.path.join("ade", "ade-annouceal.py")
    subprocess.Popen(["python", script_path])

def run_vic():
    script_path = os.path.join("vic", "vic-annouceal.py")
    subprocess.Popen(["python", script_path])

root = tk.Tk()
root.title("Annouceal Launcher")
root.geometry("300x150")

ade_button = tk.Button(root, text="Launch ADE Annouceal", command=run_ade, width=25, height=2)
vic_button = tk.Button(root, text="Launch VIC Annouceal", command=run_vic, width=25, height=2)

ade_button.pack(pady=10)
vic_button.pack(pady=10)

root.mainloop()
