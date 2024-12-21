import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import math

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, radius=20, padding=4,
                bg="#1976D2", fg="white", hoverbg="#1565C0", **kwargs):
        super().__init__(parent, **kwargs)
        self.config(bg=parent["bg"])
        self.bg = bg
        self.fg = fg
        self.hoverbg = hoverbg
        self.radius = radius
        self.padding = padding
        self.command = command
        
        # Measure text and set canvas size
        self.font = kwargs.get('font', ('Segoe UI', 10))
        test_label = tk.Label(self, text=text, font=self.font)
        test_label.grid()
        text_width = test_label.winfo_reqwidth() + padding * 2
        text_height = test_label.winfo_reqheight() + padding * 2
        test_label.destroy()
        
        self.configure(width=text_width, height=text_height, highlightthickness=0)
        self.text = text
        
        # Bind events
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
        
        self._draw()

    def _draw(self, bg=None):
        bg = bg or self.bg
        self.delete("all")
        
        # Create rounded rectangle
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        
        # Draw shape
        self.create_rounded_rect(0, 0, width, height, self.radius, fill=bg)
        
        # Add text
        self.create_text(width/2, height/2, text=self.text, fill=self.fg,
                        font=self.font)

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_enter(self, e):
        self._draw(self.hoverbg)

    def _on_leave(self, e):
        self._draw()

    def _on_click(self, e):
        if self.command:
            self.command()

class CircularProgressbar(tk.Canvas):
    def __init__(self, parent, size=100, thickness=10, **kwargs):
        super().__init__(parent, width=size, height=size, **kwargs)
        self.size = size
        self.thickness = thickness
        self.configure(bg=parent["bg"], highlightthickness=0)
        self.value = 0
        self._draw()

    def _draw(self):
        self.delete("all")
        center = self.size // 2
        radius = (self.size - self.thickness) // 2
        
        # Background circle
        self.create_arc(self.thickness, self.thickness,
                       self.size-self.thickness, self.size-self.thickness,
                       start=0, extent=359.999,
                       style="arc", width=self.thickness,
                       outline="#E0E0E0")
        
        # Progress arc
        self.create_arc(self.thickness, self.thickness,
                       self.size-self.thickness, self.size-self.thickness,
                       start=-90, extent=self.value*3.6,
                       style="arc", width=self.thickness,
                       outline="#1976D2")
        
        # Percentage text
        self.create_text(center, center,
                        text=f"{int(self.value)}%",
                        font=("Segoe UI", int(self.size/6), "bold"),
                        fill="#1976D2")

    def set_value(self, value):
        self.value = min(max(0, value), 100)
        self._draw()

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip, text=self.text, 
                      background="#2C3E50", foreground="white",
                      relief="solid", borderwidth=1,
                      font=("Segoe UI", 9),
                      padx=5, pady=2)
        label.pack()

    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class AnimatedProgressBar(ttk.Progressbar):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._value = 0
        self._target = 0
        self._speed = 2

    def set_value(self, value):
        self._target = value
        self._animate()

    def _animate(self):
        if self._value < self._target:
            self._value = min(self._value + self._speed, self._target)
            self["value"] = self._value
            self.after(10, self._animate)
        elif self._value > self._target:
            self._value = max(self._value - self._speed, self._target)
            self["value"] = self._value
            self.after(10, self._animate)

class SearchEntry(ttk.Entry):
    def __init__(self, parent, placeholder="Search...", **kwargs):
        super().__init__(parent, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = 'grey'
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

        self._add_placeholder()

    def _clear_placeholder(self, e):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self['fg'] = self.default_fg_color

    def _add_placeholder(self, e=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self['fg'] = self.placeholder_color

    def get_value(self):
        if self.get() == self.placeholder:
            return ""
        return self.get()

class NotificationBadge(tk.Canvas):
    def __init__(self, parent, size=20, **kwargs):
        super().__init__(parent, width=size, height=size, **kwargs)
        self.size = size
        self.configure(bg=parent["bg"], highlightthickness=0)
        self.value = 0
        self._draw()

    def _draw(self):
        self.delete("all")
        if self.value > 0:
            # Draw red circle
            self.create_oval(0, 0, self.size, self.size,
                           fill="#F44336", outline="")
            # Draw number
            text = str(self.value) if self.value < 100 else "99+"
            self.create_text(self.size/2, self.size/2,
                           text=text, fill="white",
                           font=("Segoe UI", int(self.size/2)))

    def set_value(self, value):
        self.value = max(0, value)
        self._draw()

# References
# 1. **Tkinter**
#    - Python's standard GUI library
#    - Used for: Main application interface
#    - Documentation: [Python Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
# 2. **Pillow**
#    - Used for: Image handling and processing
#    - Documentation: [Pillow Documentation](https://pillow.readthedocs.io/)
