import tkinter as tk
from tkinter import messagebox
import pyttsx3
import json
import os
import pygame

pygame.mixer.init()

engine = pyttsx3.init()
PROMPT_FILE = "prompts.json"
ATTENTION_SOUND = "bing.mp3"

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
        natural_voices = [v for v in self.voices if "Natural" in v.name or "Online" in v.name]
        if not natural_voices:
            natural_voices = self.voices
        voice_names = [voice.name for voice in natural_voices]
        self.voices = natural_voices

        self.selected_voice = tk.StringVar()
        self.selected_voice.set(voice_names[0])
        self.voice_menu = tk.OptionMenu(master, self.selected_voice, *voice_names)
        self.voice_menu.pack(pady=5)

        self.rate_scale = tk.Scale(master, from_=50, to=300, orient=tk.HORIZONTAL, label="Speech Rate")
        self.rate_scale.set(engine.getProperty('rate'))
        self.rate_scale.pack(pady=5)

        self.volume_scale = tk.Scale(master, from_=0, to=100, orient=tk.HORIZONTAL, label="Volume")
        self.volume_scale.set(int(engine.getProperty('volume') * 100))
        self.volume_scale.pack(pady=5)

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
            try:
                pygame.mixer.music.load(ATTENTION_SOUND)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():  # Wait for sound to finish
                    pygame.time.Clock().tick(10)
            except Exception as e:
                messagebox.showwarning("Missing sound", f"Could not play attention sound. {str(e)}")

            selected_name = self.selected_voice.get()
            for voice in self.voices:
                if voice.name == selected_name:
                    engine.setProperty('voice', voice.id)
                    break

            engine.setProperty('rate', self.rate_scale.get())
            engine.setProperty('volume', self.volume_scale.get() / 100)
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
