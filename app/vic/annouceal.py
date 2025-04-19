import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import pyttsx3
import json
import os
import pygame
from datetime import datetime

pygame.mixer.init()

engine = pyttsx3.init()
PROMPT_FILE = "prompts.json"
ATTENTION_SOUND = "bing.mp3"

CATEGORY_ICONS = {
    "Emergency": "emergency.png",
    "Major": "major.png",
    "Reminders": "reminder.png",
    "Exit": "exit.png",
    "Next Stop": "exit.png"
}

SANDRINGHAM_TO_CITY = [
    "Sandringham", "Hampton", "Brighton Beach", "Middle Brighton", "North Brighton",
    "Gardenvale", "Elsternwick", "Ripponlea", "Balaclava", "Windsor", 
    "Prahan", "Windsor", "South Yarra", "Flinders Street"
]

CITY_TO_SANDRINGHAM = list(reversed(SANDRINGHAM_TO_CITY))

WILLIAMS_TO_CITY = [
    "Williamstown", "Williamstown Beach", "North Williamstown", "Newport", "Spotswood",
    "Yarraville", "Seddon", "Footscray", "South Kensington", "Southern Cross", 
    "Flinders Street"
]

CITY_TO_WILLIAMS = list(reversed(WILLIAMS_TO_CITY))

WERRIBEE_TO_CITY = [
    "Werribee", "Hoppers Crossing", "Williams Landing", "Aircraft", "Laverton",
    "Westona", "Altona", "Seaholme", "Newport", "Spotswood",
    "Yarraville", "Seddon", "Footscray", "South Kensington", 
    "Southern Cross", "Flinders Street"
]

CITY_TO_WERRIBEE = list(reversed(WERRIBEE_TO_CITY))

FRANKS_TO_CITY = [
    "Frankston", "Kananook", "Seaford", "Carrum", "Bonbeach",
    "Chelsea", "Edithvale", "Aspendale", "Mordialloc", "Parkdale",
    "Mentone", "Cheltenham", "Southland", "Highett", "Moorabbin",
    "Patterson", "Bentleigh", "McKinnon", "Ormond", "Glenhuntly", 
    "Caulfield", "Malvern", "Armadale", "Toorak", "Hawksburn",
    "South Yarra", "Flinders Street"
]

CITY_TO_FRANKS = list(reversed(FRANKS_TO_CITY))

CRANBOURNE_TO_CITY = [
    "Cranbourne", "Merinda Park", "Lynbrook", "Dandenong", "Yarraman",
    "Noble Park", "Sandown Park", "Springvale", "Westall", "Clayton",
    "Huntingdale", "Oakleigh", "Hughesdale", "Murrumbeena", "Carnegie",
    "Caulfield", "South Yarra", "Richmond", "Flinders Street"
]

CITY_TO_CRANBOURNE = list(reversed(CRANBOURNE_TO_CITY))

PAKENHAM_TO_CITY = [
    "East Pakenham", "Pakenham", "Cardinia Road", "Officer", "Beaconsfield",
    "Berwick", "Narre Warren", "Hallam", "Dandenong", "Yarraman",
    "Noble Park", "Sandown Park", "Springvale", "Westall", "Clayton",
    "Huntingdale", "Oakleigh", "Hughesdale", "Murrumbeena", "Carnegie",
    "Caulfield", "South Yarra", "Richmond", "Flinders Street"
]

CITY_TO_PAKENHAM = list(reversed(PAKENHAM_TO_CITY))


ROUTE_CODES = {
    "Sandringham to City": 100,
    "City to Sandringham": 101,
    "Williamstown to City": 200,
    "City to Williamstown": 201,
    "Werribee to City": 202,
    "City to Werribee": 203,
    "Frankston to City": 204,
    "City to Frankston": 205,
    "Cranbourne to City": 300,
    "City to Cranbourne": 301,
    "Pakenham to City": 302,
    "City to Pakenham": 303
}

def load_prompts():
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_prompts():
    with open(PROMPT_FILE, "w") as f:
        json.dump(prompts, f, indent=4)

def smart_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning! "
    elif 12 <= hour < 17:
        return "Good afternoon! "
    elif 17 <= hour < 21:
        return "Good evening! "
    else:
        return "Good night! "

prompts = load_prompts()

class VisualAnnouncer:
    def __init__(self, text, category):
        self.window = tk.Toplevel()
        self.window.title("Visual Announcement")
        self.window.geometry("400x200")
        icon_file = CATEGORY_ICONS.get(category, "unknown.png")

        if os.path.exists(icon_file):
            image = Image.open(icon_file).resize((80, 80))
            self.icon = ImageTk.PhotoImage(image)
            self.image_label = tk.Label(self.window, image=self.icon)
            self.image_label.pack(pady=10)

        self.label = tk.Label(self.window, text=text, font=("Arial", 14), wraplength=380, justify="center")
        self.label.pack(pady=10)

        self.window.update_idletasks()
        self.window.update()

    def close(self):
        self.window.destroy()

class Annouceal:
    def __init__(self, master):
        self.master = master
        self.master.title("Annouceal")

        self.route = None
        self.route_index = -1

        route_label = tk.Label(master, text="Route Selection:")
        route_label.pack(pady=2)

        self.route_button = tk.Button(master, text="Enter Route Code", command=self.enter_route_code)
        self.route_button.pack(pady=5)

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

        self.next_stop_button = tk.Button(master, text="Next Stop", command=self.announce_next_stop)
        self.next_stop_button.pack(pady=5)
        self.next_stop_button.pack_forget()

        self.update_message_list()
        if self.categories:
            self.selected_category.set(self.categories[0])

    def enter_route_code(self):
        code = simpledialog.askinteger("Enter Route Code", "Please enter the route code:")
        if code is not None:
            self.set_route(code)

    def set_route(self, code):
        route_name = None
        for name, route_code in ROUTE_CODES.items():
            if route_code == code:
                route_name = name
                break

        if route_name is None:
            messagebox.showerror("Invalid Code", "That route code is not valid.")
            self.route = None
            self.route_index = -1
            self.next_stop_button.pack_forget()
            return


        if route_name == "Sandringham to City":
            self.route = SANDRINGHAM_TO_CITY
        elif route_name == "City to Sandringham":
            self.route = CITY_TO_SANDRINGHAM
        elif route_name == "Williamstown to City":
            self.route = WILLIAMS_TO_CITY
        elif route_name == "City to Williamstown":
            self.route = CITY_TO_WILLIAMS
        elif route_name == "Werribee to City":
            self.route = WERRIBEE_TO_CITY
        elif route_name == "City to Werribee":
            self.route = CITY_TO_WERRIBEE
        elif route_name == "Frankston to City":
            self.route = FRANKS_TO_CITY
        elif route_name == "City to Frankston":
            self.route = CITY_TO_FRANKS
        elif route_name == "Cranbourne to City":
            self.route = CRANBOURNE_TO_CITY
        elif route_name == "City to Cranbourne":
            self.route = CITY_TO_CRANBOURNE
        elif route_name == "Pakenham to City":
            self.route = PAKENHAM_TO_CITY
        elif route_name == "City to Pakenham":
            self.route = CITY_TO_PAKENHAM
        
        else:
            self.route = None

        if self.route:
            self.route_index = -1
            self.next_stop_button.pack(pady=5)
            messagebox.showinfo("Route Selected", f"Route set to {route_name}")
        else:
            self.route_index = -1
            self.next_stop_button.pack_forget()

    def announce_next_stop(self):
        if self.route is None:
            messagebox.showwarning("No Route", "Please enter a valid route code first.")
            return

        self.route_index += 1
        if self.route_index >= len(self.route):
            messagebox.showinfo("End of Route", "You have reached the final stop.")
            self.route_index = -1
            return

        station = self.route[self.route_index]
        announcement = f"This is: {station}. Please prepare to disembark."
        self.play_announcement(announcement, "Next Stop")

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
            greeting = smart_greeting()
            full_text = greeting + text
            self.play_announcement(full_text, self.selected_category.get())
        else:
            messagebox.showwarning("No message", "Please select or type a message to announce!")

    def play_announcement(self, text, category):
        try:
            pygame.mixer.music.load(ATTENTION_SOUND)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
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

        visual = VisualAnnouncer(text, category)
        engine.say(text)
        engine.runAndWait()
        visual.close()

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