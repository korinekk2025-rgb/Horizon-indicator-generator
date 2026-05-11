import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageDraw, ImageTk
import configparser


class HorizonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Artificial Horizon Generator")

        self.width_var = tk.IntVar(value=800)
        self.height_var = tk.IntVar(value=400)
        self.spacing_var = tk.IntVar(value=15)
        self.thickness_var = tk.IntVar(value=2)
        self.alpha_var = tk.IntVar(value=255)

        self.show_grid = tk.BooleanVar(value=True)
        self.show_horizon = tk.BooleanVar(value=True)

        self.top_color = "#1e90ff"
        self.bottom_color = "#f4c542"
        self.line_color = "#000000"
        self.horizon_color = "#ffffff"

        self.image = None
        self.tk_image = None

        self.build_ui()
        self.generate()

    def build_ui(self):
        left = tk.Frame(self.root)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        tk.Label(left, text="Width").pack()
        tk.Entry(left, textvariable=self.width_var).pack()

        tk.Label(left, text="Height").pack()
        tk.Entry(left, textvariable=self.height_var).pack()

        tk.Label(left, text="Line spacing").pack()
        tk.Scale(left, from_=5, to=50, orient="horizontal",
                 variable=self.spacing_var, command=lambda e: self.generate()).pack()

        tk.Label(left, text="Line thickness").pack()
        tk.Scale(left, from_=1, to=10, orient="horizontal",
                 variable=self.thickness_var, command=lambda e: self.generate()).pack()

        tk.Label(left, text="Line alpha").pack()
        tk.Scale(left, from_=0, to=255, orient="horizontal",
                 variable=self.alpha_var, command=lambda e: self.generate()).pack()

        tk.Checkbutton(left, text="Show grid",
                       variable=self.show_grid, command=self.generate).pack()

        tk.Checkbutton(left, text="Show horizon",
                       variable=self.show_horizon, command=self.generate).pack()

        tk.Button(left, text="Top color", command=self.pick_top).pack(pady=5)
        tk.Button(left, text="Bottom color", command=self.pick_bottom).pack(pady=5)
        tk.Button(left, text="Line color", command=self.pick_line).pack(pady=5)
        tk.Button(left, text="Horizon color", command=self.pick_horizon).pack(pady=5)

        tk.Button(left, text="Generate", command=self.generate).pack(pady=10)
        tk.Button(left, text="Save PNG", command=self.save).pack(pady=5)

        tk.Button(left, text="Save preset", command=self.save_preset).pack(pady=5)
        tk.Button(left, text="Load preset", command=self.load_preset).pack(pady=5)

        right = tk.Frame(self.root)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.preview_label = tk.Label(right)
        self.preview_label.pack()

    def pick_top(self):
        c = colorchooser.askcolor()[1]
        if c:
            self.top_color = c
            self.generate()

    def pick_bottom(self):
        c = colorchooser.askcolor()[1]
        if c:
            self.bottom_color = c
            self.generate()

    def pick_line(self):
        c = colorchooser.askcolor()[1]
        if c:
            self.line_color = c
            self.generate()

    def pick_horizon(self):
        c = colorchooser.askcolor()[1]
        if c:
            self.horizon_color = c
            self.generate()

    def hex_to_rgb(self, h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def generate(self):
        w = self.width_var.get()
        h = self.height_var.get()
        spacing = self.spacing_var.get()
        thickness = self.thickness_var.get()
        alpha = self.alpha_var.get()

        img = Image.new("RGBA", (w, h))
        draw = ImageDraw.Draw(img)

        mid = h // 2

        top = self.hex_to_rgb(self.top_color)
        bottom = self.hex_to_rgb(self.bottom_color)
        line = self.hex_to_rgb(self.line_color)
        horizon = self.hex_to_rgb(self.horizon_color)

        draw.rectangle([0, 0, w, mid], fill=top)
        draw.rectangle([0, mid, w, h], fill=bottom)

        if self.show_grid.get():
            y = mid
            while y >= 0:
                draw.line([(0, y), (w, y)],
                          fill=line + (alpha,),
                          width=thickness)
                y -= spacing

            y = mid
            while y <= h:
                draw.line([(0, y), (w, y)],
                          fill=line + (alpha,),
                          width=thickness)
                y += spacing

        if self.show_horizon.get():
            draw.line([(0, mid), (w, mid)],
                      fill=horizon + (255,),
                      width=thickness + 2)

        self.image = img

        preview = img.resize((400, int(400 * h / w)))
        self.tk_image = ImageTk.PhotoImage(preview.convert("RGBA"))
        self.preview_label.config(image=self.tk_image)

    def save(self):
        if not self.image:
            return

        file = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG", "*.png")])
        if file:
            self.image.save(file)
            messagebox.showinfo("Saved", "Image saved!")

    def save_preset(self):
        file = filedialog.asksaveasfilename(defaultextension=".ini",
                                            filetypes=[("INI", "*.ini")])
        if not file:
            return

        cfg = configparser.ConfigParser()

        cfg["SETTINGS"] = {
            "width": self.width_var.get(),
            "height": self.height_var.get(),
            "spacing": self.spacing_var.get(),
            "thickness": self.thickness_var.get(),
            "alpha": self.alpha_var.get(),
            "show_grid": int(self.show_grid.get()),
            "show_horizon": int(self.show_horizon.get()),
            "top_color": self.top_color,
            "bottom_color": self.bottom_color,
            "line_color": self.line_color,
            "horizon_color": self.horizon_color
        }

        with open(file, "w") as f:
            cfg.write(f)

        messagebox.showinfo("OK", "Preset saved!")

    def load_preset(self):
        file = filedialog.askopenfilename(filetypes=[("INI", "*.ini")])
        if not file:
            return

        cfg = configparser.ConfigParser()
        cfg.read(file)

        s = cfg["SETTINGS"]

        self.width_var.set(int(s["width"]))
        self.height_var.set(int(s["height"]))
        self.spacing_var.set(int(s["spacing"]))
        self.thickness_var.set(int(s["thickness"]))
        self.alpha_var.set(int(s["alpha"]))

        self.show_grid.set(int(s["show_grid"]))
        self.show_horizon.set(int(s["show_horizon"]))

        self.top_color = s["top_color"]
        self.bottom_color = s["bottom_color"]
        self.line_color = s["line_color"]
        self.horizon_color = s["horizon_color"]

        self.generate()


if __name__ == "__main__":
    root = tk.Tk()
    app = HorizonApp(root)
    root.mainloop()