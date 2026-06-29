"""Transparante game counter overlay."""

import tkinter as tk


class GameOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.8)
        self.root.configure(bg='black')
        self.root.geometry('+10+10')

        self.label = tk.Label(
            self.root,
            text="Game 0/0",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='black',
            padx=10,
            pady=5
        )
        self.label.pack()

    def update(self, current, total, status=""):
        text = f"Game {current}/{total}"
        if status:
            text += f" | {status}"
        self.label.config(text=text)
        self.root.update()

    def close(self):
        self.root.destroy()