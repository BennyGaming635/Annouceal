import tkinter as tk
from tkinter import messagebox
import pyttsx3
import json
import os

engine = pyttsx3.init()
PROMPT_FILE = "prompts.json"

def load_prompts():
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_prompts():
    with open(PROMPT_FILE, "w") as f:
        json.dump(prompts, f, indent=4)
prompts = load_prompts()

class Annouceal:
    def __init__(self, master):
        self.master = master
        self.master.title("Annouceal")
        self.categories = list(prompts.keys())
        self.selected_category = tk.StringVar()
        self.selected_category.trace('w', self.update_message_list)
        self.category_menu = tk.OptionMenu(master, self.selected_category, *self.categories)
        self.category_menu.pack(pady=5)
        self.message_listbox = tk.Listbox(master, width=50, height=8)
        self.message_listbox.pack(pady=5)
        self.custom_entry = tk.Entry(master, width=50)
        self.custom_entry.pack(pady=5)
        self.voices = engine.getProperty('voices')
        self.selected_voice = tk.StringVar()
        voice_names = [voice.name for voice in self.voices]
        self.selected_voice.set(voice_names[0])
        self.voice_menu = tk.OptionMenu(master, self.selected_voice, *voice_names)
        self.voice_menu.pack(pady=5)
        self.speak_button = tk.Button(master, text="Play", command=self.speak_message)
        self.speak_button.pack(pady=5)
        self.add_button = tk.Button(master, text="Add", command=self.add_custom_message)
        self.add_button.pack(pady=5)
        self.update_message_list()
        if self.categories:
            self.selected_category.set(self.categories[0])
    def update_message_list(self, *args):
        self.message_listbox.delete(0, tk.END)
        cat = self.selected_category.get()
        for msg in prompts.get(cat, []):
            self.message_listbox.insert(tk.END, msg)
    def speak_message(self):
        text = self.custom_entry.get().strip()
        if not text and self.message_listbox.curselection():
            index = self.message_listbox.curselection()[0]
            text = self.message_listbox.get(index)
        if text:
            selected_name = self.selected_voice.get()
            for voice in self.voices:
                if voice.name == selected_name:
                    engine.setProperty('voice', voice.id)
                    break
            engine.say(text)
            engine.runAndWait()
        else:
            messagebox.showwarning("No message", "Please select or type a message to announce!")
    def add_custom_message(self):
        text = self.custom_entry.get().strip()
        cat = self.selected_category.get()
        if not cat:
            messagebox.showwarning("No Category", "Please select a category first.")
            return
        if text:
            if cat not in prompts:
                prompts[cat] = []

            prompts[cat].append(text)
            self.message_listbox.insert(tk.END, text)
            self.custom_entry.delete(0, tk.END)
            save_prompts()
            messagebox.showinfo("Saved!", f"'{text}' was added and saved under {cat}.")
        else:
            messagebox.showwarning("Empty message", "Please type a message first!")

if __name__ == "__main__":
    root = tk.Tk()
    app = Annouceal(root)
    root.mainloop()
