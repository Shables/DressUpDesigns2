import os
import time
import tkinter as tk
from tkinter import ttk, font
from PIL import Image, ImageTk, ImageGrab

class DressUpGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Dress-Up Game")
        self.root.geometry("1080x720")

        self.custom_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.custom_font_large = font.Font(family="Helvetica", size=16, weight="bold", slant="italic")

        self.items = self.load_items("assets")
        self.current_outfit = {}

        self.setup_ui()
        self.load_base_model()

    def load_items(self, assets_dir):
        items = {}
        for category in os.listdir(assets_dir):
            category_path = os.path.join(assets_dir, category)
            if os.path.isdir(category_path):
                items[category] = []
                for item_file in os.listdir(category_path):
                    if item_file.endswith('.png'):
                        item_name = os.path.splitext(item_file)[0]
                        items[category].append(item_name)
        return items

    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)

        # Left panel
        self.left_panel = tk.Frame(main_frame, width=250, bg='Teal')
        self.left_panel.pack(side='left', fill='y')

        # Top label
        tk.Label(self.left_panel, bg='Salmon', text="Wardrobe Items", font=self.custom_font_large).pack(pady=10)

        # Category listbox
        self.create_category_listbox()

        # Scrollable canvas for item display
        canvas_frame = tk.Frame(self.left_panel, bg='Teal')
        canvas_frame.pack(fill='both', expand=True)

        self.canvas = tk.Canvas(canvas_frame, width=220, bg='Salmon')
        self.canvas.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.canvas.yview)
        scrollbar.pack(side='right', fill='y')
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.item_display_frame = tk.Frame(self.canvas, bg='Salmon')
        self.canvas.create_window((0, 0), window=self.item_display_frame, anchor='nw')

        # Bottom label
        tk.Label(self.left_panel, bg='Salmon', text="You are beautiful!", font=self.custom_font_large).pack(pady=10)

        # Dress area (right side)
        self.dress_area = tk.Canvas(main_frame, bg='LightSeaGreen')
        self.dress_area.pack(side='right', fill='both', expand=True)

        # Screenshot button
        self.screenshot_button = ttk.Button(self.dress_area, text="Take Screenshot", command=self.take_screenshot)
        self.screenshot_button.place(relx=0.05, rely=0.05, anchor='nw')

        # Bind the canvas configure event
        self.item_display_frame.bind("<Configure>", self.on_frame_configure)

    def create_category_listbox(self):
        self.category_listbox = tk.Listbox(self.left_panel, font=self.custom_font_large, width=20, bg='medium orchid')
        for category in self.items.keys():
            self.category_listbox.insert(tk.END, self.center_text(category, 20))
        self.category_listbox.pack(pady=10, padx=10, fill='x')
        self.category_listbox.bind('<<ListboxSelect>>', self.on_category_select)

    @staticmethod
    def center_text(text, width):
        return text.center(width)

    def load_base_model(self):
        self.base_model = Image.open("assets/Complete Base Model v1.png")
        self.base_model_photo = ImageTk.PhotoImage(self.base_model)

        x = (830 - self.base_model.width) // 2
        y = (700 - self.base_model.height) // 2

        self.base_model_item = self.dress_area.create_image(x, y, image=self.base_model_photo, anchor=tk.NW)

    def on_category_select(self, event):
        selected_indices = self.category_listbox.curselection()
        if selected_indices:
            selected_category = self.category_listbox.get(selected_indices[0]).strip()
            self.display_category_items(selected_category)

    def display_category_items(self, category):
        for widget in self.item_display_frame.winfo_children():
            widget.destroy()

        for i, item_name in enumerate(self.items[category]):
            image_path = f"assets/{category.lower()}/{item_name}.png"
            if os.path.exists(image_path):
                image = self.load_image(image_path)
                if image:
                    button = tk.Button(self.item_display_frame, image=image, text=item_name, compound=tk.TOP)
                    button.image = image
                    button.grid(row=i // 2, column=i % 2, padx=5, pady=5)
                    button.bind('<Button-1>', lambda e, c=category, i=item_name: self.on_item_click(c, i))
            else:
                print(f"Image file not found: {image_path}")

        self.item_display_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    @staticmethod
    def load_image(file_path, size=(100, 100)):
        try:
            image = Image.open(file_path)
            image = image.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        except FileNotFoundError:
            print(f"Image file not found: {file_path}")
            return None

    def on_item_click(self, category, item_name):
        if category in self.current_outfit:
            self.dress_area.delete(self.current_outfit[category])

        image_path = f"assets/{category.lower()}/{item_name}.png"
        if os.path.exists(image_path):
            item_image = Image.open(image_path)
            item_photo = ImageTk.PhotoImage(item_image)

            x = (830 - item_image.width) // 2
            y = (700 - item_image.height) // 2

            item = self.dress_area.create_image(x, y, image=item_photo, anchor=tk.NW)
            self.current_outfit[category] = item

            # Keep a reference to avoid garbage collection
            setattr(self, f"{category}_{item_name}_photo", item_photo)

            self.reorder_items()

    def reorder_items(self):
        category_order = ['BOTTOMS', 'TOPS', 'HANDS', 'FEET', 'HEADS', 'HAIRS', 'EYES', 'LIPS', 'BANGS']
        for category in category_order:
            if category in self.current_outfit:
                self.dress_area.tag_raise(self.current_outfit[category])
        self.dress_area.tag_lower(self.base_model_item)

    def take_screenshot(self):
        os.makedirs("screenshots", exist_ok=True)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"screenshots/dressup_{timestamp}.png"

        x = self.dress_area.winfo_rootx() + self.dress_area.winfo_x()
        y = self.dress_area.winfo_rooty() + self.dress_area.winfo_y()
        width = self.dress_area.winfo_width()
        height = self.dress_area.winfo_height() 

        screenshot = ImageGrab.grab(bbox=(x, y, x+width, y+height))
        screenshot.save(filename)
        print(f"Screenshot saved as {filename}")

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

if __name__ == "__main__":
    root = tk.Tk()
    game = DressUpGame(root)
    root.mainloop()