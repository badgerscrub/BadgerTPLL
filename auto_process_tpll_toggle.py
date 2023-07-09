import re
import clipboard
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import time
import pygetwindow
import pyautogui
from tkinter import ttk
from ttkthemes import ThemedTk
import keyboard

# Declare global variables
stop_event = None
processed_clipboard_data = None

def clean_clipboard_data():
    clipboard_data = clipboard.paste()

    # Remove extra spaces
    cleaned_data = re.sub(r'\s+', ' ', clipboard_data.strip())

    # Remove degree symbols
    cleaned_data = re.sub(r'°', '', cleaned_data)

    # Format the coordinates in "/tpll xx.xxxxxx xx.xxxxxx" format
    match = re.match(r'(\d+\.\d+)\s+(-?\d+\.\d+)', cleaned_data)
    if match:
        cleaned_data = "/tpll {} {}".format(match.group(1), match.group(2))

    clipboard.copy(cleaned_data)

    return cleaned_data

def process_coordinates(cleaned_data):
    if not toggle_minecraft.get():
        return

    # Keep checking for Minecraft window and whether the keys are pressed
    while True:
        # Get the Minecraft window with the exact title
        minecraft_windows = pygetwindow.getWindowsWithTitle("Minecraft 1.12.2 - BuildTheEarth")
        
        if len(minecraft_windows) == 0:
            terminal.insert(tk.END, "Minecraft window not found.\n\n")
            terminal.see(tk.END)  # Scroll to the end
            return
        
        minecraft_window = minecraft_windows[0]
        minecraft_window.activate()
        
        # Pause to ensure focus on Minecraft window
        time.sleep(0.25)

        # If the 'Ctrl' and 'Shift' keys are not being pressed, break the loop
        if not (keyboard.is_pressed('shift') and keyboard.is_pressed('ctrl')):
            break

        # If the keys are still being pressed, wait a short time before the next loop iteration
        time.sleep(0.1)
    
    # Automate Minecraft actions
    pyautogui.press("esc")  # Unpause the game
    time.sleep(0.1)
    pyautogui.press("enter")  # Open chat
    time.sleep(0.1)
    pyautogui.typewrite(cleaned_data)  # Paste coordinates
    time.sleep(0.1)
    pyautogui.press("enter")  # Send chat message

def monitor_clipboard(terminal):
    global stop_event

    last_processed_clipboard_data = clipboard.paste()
    processed_clipboard_data = None

    while not stop_event.is_set():
        clipboard_data = clipboard.paste()

        if clipboard_data != last_processed_clipboard_data:
            last_processed_clipboard_data = clipboard_data

            # Check if the clipboard data matches the coordinate pattern
            match = re.match(r'\s*(-?\d+\.\d+)\s*[°\s,]+\s*(-?\d+\.\d+)', clipboard_data)
            if match:
                cleaned_data = "/tpll {} {}".format(match.group(1), match.group(2))

                terminal.insert(tk.END, "Your coordinates have been copied.\n")
                terminal.insert(tk.END, "Original Coordinates: {}\n".format(clipboard_data))
                terminal.insert(tk.END, "Cleaned Coordinates: {}\n\n".format(cleaned_data))
                terminal.see(tk.END)  # Scroll to the end

                # Process the coordinates in Minecraft
                process_coordinates(cleaned_data)

                # Store the processed coordinates
                processed_clipboard_data = clipboard_data
            else:
                terminal.insert(tk.END, "Invalid clipboard entry. Coordinates not detected.\n\n")
                terminal.see(tk.END)  # Scroll to the end

        time.sleep(0.2)


def start_monitoring(terminal):
    global stop_event

    terminal.insert(tk.END, "Starting /tpll translator...\n")

    stop_event = threading.Event()

    # Start the clipboard monitoring thread
    monitor_thread = threading.Thread(target=monitor_clipboard, args=(terminal,))
    monitor_thread.start()

def stop_monitoring(terminal):
    global stop_event

    if stop_event is not None:
        terminal.insert(tk.END, "Stopping /tpll translator...\n")
        stop_event.set()
    else:
        terminal.insert(tk.END, "Monitoring is not active.\n")





def change_theme(theme):
    window.set_theme(theme)

# Create the GUI window
window = ThemedTk(theme="equilux")
window.title("Google Earth to /tpll Translator")

# Create a root frame that will inherit the theme and contain all widgets
root_frame = ttk.Frame(window)
root_frame.pack(fill=tk.BOTH, expand=True)

def on_window_close():
    stop_monitoring(terminal)
    window.destroy()

# Bind the window close event
window.protocol("WM_DELETE_WINDOW", on_window_close)

# Create the terminal window
terminal_label = ttk.Label(root_frame, text="Terminal:", font=("Arial", 12))
terminal_label.pack()
terminal_frame = ttk.Frame(root_frame)
terminal_frame.pack(expand=True, fill=tk.BOTH)
terminal = tk.Text(terminal_frame, height=10, wrap=tk.WORD, font=("Arial", 12))
terminal.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar = ttk.Scrollbar(terminal_frame, command=terminal.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
terminal['yscrollcommand'] = scrollbar.set

# Create a frame for buttons
button_frame = ttk.Frame(root_frame)
button_frame.pack(pady=10)

# Create the start button
start_button = ttk.Button(button_frame, text="Start", command=lambda: start_monitoring(terminal))
start_button.pack(side=tk.LEFT, padx=10)

# Create the stop button
stop_button = ttk.Button(button_frame, text="Stop", command=lambda: stop_monitoring(terminal))
stop_button.pack(side=tk.LEFT, padx=10)

# Create the toggle button for Minecraft function
toggle_minecraft = tk.BooleanVar()
toggle_minecraft_button = ttk.Checkbutton(button_frame, text="Toggle Minecraft Pasting Automation", variable=toggle_minecraft)
toggle_minecraft_button.pack(side=tk.LEFT, padx=10)

# Create a frame for theme selection
theme_frame = ttk.Frame(root_frame)
theme_frame.pack(pady=10)

# Create the theme selection dropdown
selected_theme = tk.StringVar()
theme_dropdown = ttk.OptionMenu(theme_frame, selected_theme, "adapta", "aquativo", "arc", "black", "blue", "breeze", "clearlooks", "elegance", "equilux", "keramik", "kroc", "plastik", "radiance", "smog", "winxpblue", "yaru", command=change_theme)
theme_dropdown.config(width=15)
theme_dropdown.pack(side=tk.LEFT, padx=10)

# Create a label for the theme selection
theme_label = ttk.Label(theme_frame, text="Theme Selection:", font=("Arial", 12))
theme_label.pack(side=tk.LEFT)

# Configure resizing behavior
window.columnconfigure(0, weight=1)
window.rowconfigure(1, weight=1)

# Start the GUI event loop
window.mainloop()