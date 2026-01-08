import threading
import time
import tkinter as tk
from pynput.keyboard import Controller, Key

keyboard = Controller()
running = False
worker_thread = None
press_count = 0
key_index = 0
is_minimized = False


def toggle_macro():
    global running, worker_thread, press_count, key_index

    if running:
        running = False
        update_button()
        return

    raw_keys = key_entry.get().strip()
    delay = delay_entry.get().strip()

    if not raw_keys:
        set_status("Enter at least one key")
        return
    if not delay:
        set_status("Enter a delay")
        return

    try:
        delay = float(delay)
    except ValueError:
        set_status("Delay must be a number")
        return

    keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
    if not keys:
        set_status("Invalid key list")
        return

    clear_status()
    press_count = 0
    key_index = 0
    update_stats()

    running = True
    update_button()

    def run():
        global running, press_count, key_index
        first_press = True

        while running:
            if root.focus_displayof() is None:
                press_key(keys[key_index])
                press_count += 1
                update_stats()
                key_index = (key_index + 1) % len(keys)

                if first_press:
                    first_press = False
                else:
                    time.sleep(delay)
            else:
                time.sleep(0.05)

    worker_thread = threading.Thread(target=run, daemon=True)
    worker_thread.start()

def press_key(key_name):
    try:
        if hasattr(Key, key_name):
            key = getattr(Key, key_name)
            keyboard.press(key)
            keyboard.release(key)
        else:
            keyboard.press(key_name)
            keyboard.release(key_name)
    except:
        pass

def set_status(text):
    status_label.config(text=text)

def clear_status():
    status_label.config(text="")

def update_stats():
    stats_label.config(text=f"Key presses: {press_count}")

BG        = "#15151a"
FIELD_BG = "#1e1e24"
TEXT      = "#e6e6eb"
MUTED     = "#9a9aa3"
ACCENT    = "#8b8bff"
ERROR     = "#f87171"

FONT = ("Segoe UI", 10)


root = tk.Tk()
root.overrideredirect(True)
root.geometry("380x425")
root.configure(bg=BG)
root.attributes("-topmost", True)


def start_drag(e):
    root.x = e.x_root
    root.y = e.y_root

def do_drag(e):
    dx = e.x_root - root.x
    dy = e.y_root - root.y
    x = root.winfo_x() + dx
    y = root.winfo_y() + dy
    root.geometry(f"+{x}+{y}")
    root.x = e.x_root
    root.y = e.y_root

def bind_drag(widget):
    widget.bind("<Button-1>", start_drag)
    widget.bind("<B1-Motion>", do_drag)

def minimize():
    global is_minimized
    is_minimized = True
    root.overrideredirect(False)
    root.iconify()

def on_restore(event=None):
    global is_minimized
    if is_minimized:
        root.after(10, restore_window)

def restore_window():
    global is_minimized
    root.overrideredirect(True)
    root.deiconify()
    is_minimized = False

root.bind("<Visibility>", on_restore)




title_bar = tk.Frame(root, bg=BG, height=45)
title_bar.pack(fill="x")

title_label = tk.Label(
    title_bar,
    text="Keyboard Smasher v1.0",
    bg=BG,
    fg=TEXT,
    font=("Segoe UI Semibold", 10)
)
title_label.pack(side="left", padx=18)

btn_frame = tk.Frame(title_bar, bg=BG)
btn_frame.pack(side="right", padx=10)

min_btn = tk.Button(
    btn_frame,
    text="—",
    bg=BG,
    fg=MUTED,
    relief="flat",
    command=minimize,
    font=("Segoe UI", 12),
    cursor="hand2"
)
min_btn.pack(side="left", padx=(0, 8))

close_btn = tk.Button(
    btn_frame,
    text="✕",
    bg=BG,
    fg=MUTED,
    relief="flat",
    command=root.destroy,
    font=("Segoe UI", 11),
    cursor="hand2"
)
close_btn.pack(side="left")

bind_drag(title_bar)
bind_drag(title_label)

content = tk.Frame(root, bg=BG)
content.pack(fill="both", expand=True)

def padded_entry(parent):
    frame = tk.Frame(parent, bg=FIELD_BG)
    entry = tk.Entry(
        frame,
        bg=FIELD_BG,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat",
        font=FONT
    )
    entry.pack(fill="both", padx=8, pady=6)
    return frame, entry

tk.Label(
    content, text="Keys (comma separated)",
    bg=BG, fg=MUTED, font=FONT
).pack(anchor="w", padx=32, pady=(22, 0))

key_frame, key_entry = padded_entry(content)
key_frame.pack(fill="x", padx=32, pady=(6, 16))

tk.Label(
    content, text="Delay (seconds)",
    bg=BG, fg=MUTED, font=FONT
).pack(anchor="w", padx=32)

delay_frame, delay_entry = padded_entry(content)
delay_entry.insert(0, "1")
delay_frame.pack(fill="x", padx=32, pady=(6, 22))

btn_canvas = tk.Canvas(
    content,
    width=220,
    height=44,
    bg=BG,
    highlightthickness=0,
    cursor="hand2"
)
btn_canvas.pack(pady=(0, 18))

def draw_button(text, outline):
    btn_canvas.delete("all")

    btn_canvas.create_round_rect = lambda x1, y1, x2, y2, r, **kw: (
        btn_canvas.create_polygon(
            x1+r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1,
            smooth=True,
            **kw
        )
    )

    btn_canvas.create_round_rect(
        2, 2, 218, 42, 18,
        outline=outline,
        width=2,
        fill=""
    )

    btn_canvas.create_text(
        110, 22,
        text=text,
        fill=outline,
        font=("Segoe UI Semibold", 10)
    )

def on_button_click(event):
    toggle_macro()

btn_canvas.bind("<Button-1>", on_button_click)

def update_button():
    if running:
        draw_button("Stop", ERROR)
    else:
        draw_button("Start", ACCENT)

update_button()

status_label = tk.Label(
    content,
    text="",
    bg=BG,
    fg=ERROR,
    font=("Segoe UI", 9)
)
status_label.pack()

stats_label = tk.Label(
    content,
    text="Key presses: 0",
    bg=BG,
    fg=MUTED,
    font=("Segoe UI", 9)
)
stats_label.pack(pady=(6, 18))

tk.Label(
    content,
    text="Made by GSRHaX",
    bg=BG,
    fg="#555",
    font=("Segoe UI", 9)
).pack(pady=(0, 16))

root.mainloop()
