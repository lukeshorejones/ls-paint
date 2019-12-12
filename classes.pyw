import tkinter as tk

class Sidebar:
    def __init__(self, label_text, side, anchor, fill, width=0):
        self.frame = tk.Frame(bg="white", width=width)
        self.label = tk.Label(self.frame, bg="white", text=label_text)

        self.label.grid(sticky=tk.W, columnspan=2)
        self.frame.pack(side=side, anchor=anchor, fill=fill)
