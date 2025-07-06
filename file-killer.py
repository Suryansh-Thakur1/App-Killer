import tkinter as tk
from tkinter import ttk
import psutil
import os
import ctypes

# --- Helper functions ---
def is_important_process(name):
    important_keywords = ["system", "wininit", "winlogon", "csrss", "lsass", "services", "smss", "svchost", "explorer", "python"]
    return any(kw.lower() in name.lower() for kw in important_keywords)

def get_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.info
            processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sorted(processes, key=lambda x: x['cpu_percent'] + x['memory_percent'], reverse=True)

def kill_process(pid):
    try:
        p = psutil.Process(pid)
        p.terminate()
    except Exception as e:
        print(f"Couldn't kill PID {pid}: {e}")

# --- GUI Setup ---
root = tk.Tk()
root.title("Slightly Sketchy Process Killer")
root.geometry("850x600")
root.configure(bg='#1e1e1e')

checkbox_vars = []
checkbox_widgets = []
rows = []

# --- Functions ---
def refresh():
    for widget in frame.winfo_children():
        widget.destroy()
    checkbox_vars.clear()
    rows.clear()
    checkbox_widgets.clear()

    processes = get_processes()
    if not processes:
        tk.Label(frame, text="Bruh... nothing here", fg='red', bg=bg_color).pack()
        return

    for proc in processes:
        var = tk.BooleanVar()
        checkbox_vars.append((var, proc['pid']))

        frame_row = tk.Frame(frame, bg=bg_color, highlightthickness=1, highlightbackground="gray", bd=5)
        row_text = f"{proc['name']} | PID: {proc['pid']} | CPU: {proc['cpu_percent']:.1f}% | MEM: {proc['memory_percent']:.1f}%"

        label_fg = 'red' if is_important_process(proc['name']) else 'white'
        checkbox = tk.Checkbutton(frame_row, text=row_text, variable=var, fg=label_fg, bg=bg_color, selectcolor=bg_color, activebackground=bg_color)
        checkbox.pack(anchor='w')
        checkbox_widgets.append(checkbox)
        frame_row.pack(fill='x', padx=2, pady=1)

        rows.append((frame_row, proc))

def search(*args):
    query = search_var.get().lower()
    for i, (row, proc) in enumerate(rows):
        if query in proc['name'].lower():
            row.pack(fill='x', padx=2, pady=1)
        else:
            row.pack_forget()

def toggle_dark():
    global bg_color
    bg_color = '#f0f0f0' if bg_color == '#1e1e1e' else '#1e1e1e'
    root.configure(bg=bg_color)
    frame.configure(bg=bg_color)
    for widget in frame.winfo_children():
        widget.configure(bg=bg_color)
    refresh()

def yeet_selected():
    for var, pid in checkbox_vars:
        if var.get():
            kill_process(pid)
    refresh()

def nuke_all():
    for var, pid in checkbox_vars:
        proc_name = next((p['name'] for p in get_processes() if p['pid'] == pid), "")
        if not is_important_process(proc_name):
            kill_process(pid)
    refresh()

def boost_performance():
    current_pid = os.getpid()
    for proc in get_processes():
        if is_important_process(proc['name']) or proc['pid'] == current_pid:
            continue
        if proc['cpu_percent'] < 5 and proc['memory_percent'] < 5:
            kill_process(proc['pid'])
    refresh()

# --- UI Layout ---
bg_color = '#1e1e1e'

search_var = tk.StringVar()
search_var.trace_add('write', search)

search_entry = tk.Entry(root, textvariable=search_var, bg='#333333', fg='white')
search_entry.insert(0, 'Search for processes')
search_entry.pack(fill='x', padx=5, pady=5)

btn_toggle = tk.Button(root, text="Toggle Dark Mode", command=toggle_dark)
btn_toggle.pack(pady=2)

canvas = tk.Canvas(root, bg=bg_color, highlightthickness=0)
scrollbar = tk.Scrollbar(root, orient='vertical', command=canvas.yview)
frame = tk.Frame(canvas, bg=bg_color)

frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas_frame = canvas.create_window((0, 0), window=frame, anchor='nw')
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side='left', fill='both', expand=True)
scrollbar.pack(side='right', fill='y')

# --- Buttons ---
side_frame = tk.Frame(root, bg=bg_color)
side_frame.pack(side='right', fill='y')

tk.Button(side_frame, text="Refresh List", command=refresh).pack(pady=2)
tk.Button(side_frame, text="Yeet Selected", command=yeet_selected).pack(pady=2)
tk.Button(side_frame, text="Nuke All (Except System)", command=nuke_all).pack(pady=2)
tk.Button(side_frame, text="Boost Performance", command=boost_performance).pack(pady=2)

refresh()
root.mainloop()

