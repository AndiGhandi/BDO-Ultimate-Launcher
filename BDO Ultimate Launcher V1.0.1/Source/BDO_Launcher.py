"""
BDO Ultimate Launcher
Created by AndiGhandi https://github.com/AndiGhandi

GitHub:
https://github.com/DEINNAME/BDO-Ultimate-Launcher

License:
MIT License with Attribution Requirement
"""





import os
import sys
import ctypes
import subprocess
import webbrowser
import platform

import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import ctypes
from ctypes import wintypes

CONFIG_FILE = "config.ini"

APP_FOLDER = os.path.join(
    os.environ["APPDATA"],
    "BDO Ultimate Launcher"
)

os.makedirs(APP_FOLDER, exist_ok=True)

CONFIG_PATH = os.path.join(
    APP_FOLDER,
    CONFIG_FILE
)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = BASEDIR

    return os.path.join(base_path, relative_path)


# =====================================
# ADMIN ELEVATION
# =====================================

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        " ".join(sys.argv),
        None,
        1
    )
    sys.exit()

# =====================================
# BASE DIRECTORY
# =====================================

if getattr(sys, "frozen", False):
    BASEDIR = os.path.dirname(sys.executable)
else:
    BASEDIR = os.path.dirname(os.path.abspath(__file__))

# =====================================
# GPU DETECTION
# =====================================

def get_gpu_name():
    try:
        result = subprocess.check_output(
            [
                "powershell",
                "-Command",
                "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"
            ],
            text=True
        )

        for line in result.splitlines():
            if "NVIDIA" in line:
                return line.strip()

        return "No NVIDIA GPU"

    except:
        return "GPU Detection Failed"

GPU_NAME = get_gpu_name()

HAS_NVIDIA = "NVIDIA" in GPU_NAME.upper()

# =====================================
# CPU DETECTION
# =====================================

def get_cpu_name():
    try:
        result = subprocess.check_output(
            [
                "powershell",
                "-Command",
                "(Get-CimInstance Win32_Processor).Name"
            ],
            text=True
        )

        return result.strip()

    except:
        return "CPU Detection Failed"

CPU_NAME = get_cpu_name()
if len(CPU_NAME) > 35:
    CPU_NAME = CPU_NAME[:35] + "..."


# =====================================
# CONFIG
# =====================================

def save_config():
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(f"GAMEPATH={gamepath_var.get()}\n")
        f.write(f"AFFINITY={affinity_var.get()}\n")
        f.write(f"USE_STEAM={int(steam_var.get())}\n")
        f.write(f"PROFILE={profile_var.get()}\n")
        f.write(f"USE_NVIDIA={int(nvidia_var.get())}\n")
        f.write(f"USE_AFFINITY={int(affinity_enabled_var.get())}\n")
        

    messagebox.showinfo(
        "Success",
        "Configuration saved successfully!"
    )


def create_default_config():

    path = CONFIG_PATH

    with open(path, "w", encoding="utf-8") as f:
        f.write("GAMEPATH=\n")
        f.write("AFFINITY=555\n")
        f.write("USE_STEAM=1\n")
        f.write("PROFILE=smooth_off.nip\n")
        f.write("USE_NVIDIA=1\n")
        f.write("USE_AFFINITY=1\n")


def load_config():

    path = CONFIG_PATH

    if not os.path.exists(path):
        create_default_config()

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" not in line:
                continue

            key, value = line.strip().split("=", 1)

            if key == "GAMEPATH":
                gamepath_var.set(value)

            elif key == "AFFINITY":
                affinity_var.set(value)

            elif key == "USE_STEAM":
                steam_var.set(value == "1")
                
            elif key == "USE_NVIDIA":
                nvidia_var.set(value == "1")
                
            elif key == "USE_AFFINITY":
                affinity_enabled_var.set(value == "1")  

            elif key == "PROFILE":
                profile_var.set(value)

# =====================================
# PROFILE DETECTION
# =====================================

def detect_profiles():

    profiles = []

    builtin_profiles = [
        "smooth_off.nip",
        "smooth_on.nip",
        "SEMIPOTATO.nip",
        "GIGAPOTATO.nip"
    ]

    for profile in builtin_profiles:

        if os.path.exists(resource_path(profile)):
            profiles.append(profile)

    return profiles


# =====================================
# BROWSE
# =====================================

def browse_gamepath():
    path = filedialog.askdirectory()

    if path:
        gamepath_var.set(path)

# =====================================
# GUIDE
# =====================================

def open_affinity_guide():
    webbrowser.open(
        "https://docs.google.com/document/d/1cyLaDiPL_B6nOZw_qPE_wOGuoeRT-qddTjevTFoFBkg/view?tab=t.0#heading=h.rl325eap4pk9"
    )

# =====================================
# LAUNCH
# =====================================

def launch_game():

    profile = profile_var.get()

    inspector = resource_path(
        "nvidiaProfileInspector.exe"
    )

    profile_file = resource_path(
        profile
    )

    gamepath = gamepath_var.get()

    launcher = os.path.join(
        gamepath,
        "BlackDesertLauncher.exe"
    )

    if not os.path.exists(launcher):
        messagebox.showerror(
            "Error",
            "BlackDesertLauncher.exe not found!"
        )
        return

    # NVIDIA Profile Import (optional)
    if nvidia_var.get():

        if not os.path.exists(inspector):
            messagebox.showerror(
                "Error",
                "nvidiaProfileInspector.exe not found!"
            )
            return

        if not os.path.exists(profile_file):
            messagebox.showerror(
                "Error",
                "Profile not found!"
            )
            return

        try:
            subprocess.call([
                inspector,
                "-silentImportProfile",
                profile_file
            ])

        except Exception as e:
            messagebox.showerror(
                "Import Error",
                str(e)
            )
            return

    steam_arg = " -Steam" if steam_var.get() else ""

    # CPU Affinity optional
    if affinity_enabled_var.get():

        launch_cmd = (
            f'start "" /affinity {affinity_var.get()} '
            f'"{launcher}"{steam_arg}'
        )

    else:

        launch_cmd = (
            f'start "" "{launcher}"{steam_arg}'
        )

    subprocess.Popen(
        launch_cmd,
        shell=True
    )

# =====================================
# WINDOW
# =====================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("BDO Ultimate Launcher")

import ctypes

myappid = "BDOUltimateLauncher.1.0"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

root.geometry("1024x1024")
root.resizable(True, True)
root.minsize(900, 900)
root.maxsize(1024, 1024)

root.overrideredirect(True)

# Icon
# ico = os.path.join(BASEDIR, "BDOStart.ico")
ico = resource_path("BDOStart.ico")


if os.path.exists(ico):
    try:
        root.iconbitmap(ico)
    except:
        pass

# =====================================
# DRAG WINDOW
# =====================================

def start_move(event):

    root._drag_start_x = root.winfo_pointerx()
    root._drag_start_y = root.winfo_pointery()

    root._window_start_x = root.winfo_x()
    root._window_start_y = root.winfo_y()


def move_window(event):

    dx = root.winfo_pointerx() - root._drag_start_x
    dy = root.winfo_pointery() - root._drag_start_y

    root.geometry(
        f"+{root._window_start_x + dx}+{root._window_start_y + dy}"
    )

#root.bind("<Button-1>", start_move)
#root.bind("<B1-Motion>", move_window)



root.bind("<Escape>", lambda e: root.destroy())

# =====================================
# BACKGROUND IMAGE
# =====================================

#bg_file = os.path.join(BASEDIR, "background.png")

bg_file = resource_path("background.png")

bg_img = ctk.CTkImage(
    light_image=Image.open(bg_file),
    dark_image=Image.open(bg_file),
    size=(1024, 1024)
)

bg_label = ctk.CTkLabel(
    root,
    text="",
    image=bg_img
)

bg_label.place(x=0, y=0)

bg_label.bind("<Button-1>", start_move)
bg_label.bind("<B1-Motion>", move_window)

# =====================================
# LEFT PANEL
# =====================================

left_panel = ctk.CTkFrame(
    root,
    width=255,
    height=565,
    corner_radius=25,
    fg_color="#080808"
)

left_panel.place(x=80, y=120)

# =====================================
# TITLE
# =====================================
#
#title = ctk.CTkLabel(
#    left_panel,
#    text="BDO Ultimate Launcher",
#    font=("Segoe UI", 26, "bold"),
#    text_color="#D4AF37"
#)
#
#title.place(x=10, y=10)

# =====================================
# CLOSE BUTTON
# =====================================

close_btn = ctk.CTkButton(
    root,
    text="✕",
    width=15,
    height=15,
    fg_color="#8B0000",
    hover_color="#5e2028",
    command=root.destroy
)

close_btn.place(x=915, y=100)

# =====================================
# GPU & CPU
# =====================================

gpu_label = ctk.CTkLabel(
    left_panel,
    text=(
        f"GPU\n{GPU_NAME}\n\n"
        f"CPU\n{CPU_NAME}"
    ),
    justify="left",
    font=("Segoe UI", 14, "bold"),
    text_color="#D4AF37"
)

gpu_label.place(x=10, y=15)

# =====================================
# DIRECTORY
# =====================================

dir_label = ctk.CTkLabel(
    left_panel,
    text=f"Launcher Directory\n{BASEDIR}",
    justify="left",
    wraplength=280,
    font=("Segoe UI", 14, "bold"),
    text_color="#D4AF37"
)

dir_label.place(x=10, y=115)

# =====================================
# GAME PATH
# =====================================

gamepath_var = ctk.StringVar()

gamepath_label = ctk.CTkLabel(
    left_panel,
    text="Game Path",
    font=("Segoe UI", 14, "bold"),
    text_color="#D4AF37"
)

gamepath_label.place(x=10, y=170)

gamepath_entry = ctk.CTkEntry(
    left_panel,
    width=220,
    textvariable=gamepath_var
)

gamepath_entry.place(x=10, y=200)

browse_btn = ctk.CTkButton(
    left_panel,
    text="Browse",
    width=100,
    command=browse_gamepath
)

browse_btn.place(x=10, y=240)

# =====================================
# AFFINITY
# =====================================

affinity_var = ctk.StringVar(value="555")

affinity_label = ctk.CTkLabel(
    left_panel,
    text="CPU Affinity",
    font=("Segoe UI", 14, "bold"),
    text_color="#D4AF37"
)

affinity_label.place(x=10, y=285)

affinity_entry = ctk.CTkEntry(
    left_panel,
    width=70,
    textvariable=affinity_var
)

affinity_entry.place(x=10, y=315)

guide = ctk.CTkLabel(
    left_panel,
    text="CPU Affinity Guide",
    text_color="#55AAFF",
    cursor="hand2"
)

guide.place(x=10, y=355)

guide.bind(
    "<Button-1>",
    lambda e: open_affinity_guide()
)

# =====================================
# VARIABLES
# =====================================

steam_var = ctk.BooleanVar(value=True)
nvidia_var = ctk.BooleanVar(value=True)
affinity_enabled_var = ctk.BooleanVar(value=True)

# =====================================
# STEAM
# =====================================


steam_checkbox = ctk.CTkCheckBox(
    left_panel,
    text="Launch via Steam",
    variable=steam_var
)

steam_checkbox.place(x=10, y=395)

# =====================================
# NVIDIA
# =====================================

nvidia_checkbox = ctk.CTkCheckBox(
    left_panel,
    text="Use NVIDIA Profile Inspector",
    variable=nvidia_var
)

nvidia_checkbox.place(x=10, y=430)


# =====================================
# NVIDIA
# =====================================

affinity_checkbox = ctk.CTkCheckBox(
    left_panel,
    text="Use CPU Affinity",
    variable=affinity_enabled_var
)

affinity_checkbox.place(x=100, y=315)

if not HAS_NVIDIA:
    nvidia_checkbox.configure(state="disabled")



# =====================================
# PROFILES
# =====================================

profiles = detect_profiles()

if not profiles:
    profiles = ["No .nip files found"]

default_profile = "smooth_off.nip"

if default_profile not in profiles:
    default_profile = profiles[0]

profile_var = ctk.StringVar(value=default_profile)

profile_label = ctk.CTkLabel(
    left_panel,
    text="Profile",
    font=("Segoe UI", 14, "bold"),
    text_color="#D4AF37"
)

profile_label.place(x=10, y=455)

profile_dropdown = ctk.CTkOptionMenu(
    left_panel,
    values=profiles,
    variable=profile_var,
    width=220
)

profile_dropdown.place(x=10, y=480)

# =====================================
# SAVE
# =====================================

save_btn = ctk.CTkButton(
    left_panel,
    text="Save Configuration",
    width=220,
    command=save_config
)

save_btn.place(x=10, y=515)

# =====================================
# LAUNCH
# =====================================

launch_btn = ctk.CTkButton(
    root,
    text="Launch Game",
    width=360,
    height=95,
    font=("Segoe UI", 28, "bold"),
    fg_color="#D4AF37",
    text_color="black",
    hover_color="#E6C24A",
    command=launch_game
)

launch_btn.place(x=530, y=805)

# =====================================
# FOOTER
# =====================================

footer = ctk.CTkLabel(
    root,
    text="BDO Ultimate Launcher v1.0.1 by Ghandi",
    text_color="#AAAAAA",
    font=("Segoe UI", 12)
)

footer.place(x=565, y=960)




def apply_window_shape():

    hwnd = root.winfo_id()

    img = Image.open(bg_file).convert("RGBA")

    region = None

    width, height = img.size

    for y in range(height):

        start_x = None

        for x in range(width):

            alpha = img.getpixel((x, y))[3]

            if alpha > 10:

                if start_x is None:
                    start_x = x

            else:

                if start_x is not None:

                    rect = ctypes.windll.gdi32.CreateRectRgn(
                        start_x,
                        y,
                        x,
                        y + 1
                    )

                    if region is None:
                        region = rect
                    else:
                        ctypes.windll.gdi32.CombineRgn(
                            region,
                            region,
                            rect,
                            2
                        )

                    start_x = None

        if start_x is not None:

            rect = ctypes.windll.gdi32.CreateRectRgn(
                start_x,
                y,
                width,
                y + 1
            )

            if region is None:
                region = rect
            else:
                ctypes.windll.gdi32.CombineRgn(
                    region,
                    region,
                    rect,
                    2
                )

    ctypes.windll.user32.SetWindowRgn(
        hwnd,
        region,
        True
    )


# =====================================
# LOAD CONFIG
# =====================================

load_config()

root.update_idletasks()
GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080

hwnd = ctypes.windll.user32.GetParent(root.winfo_id())

style = ctypes.windll.user32.GetWindowLongW(
    hwnd,
    GWL_EXSTYLE
)

style = style & ~WS_EX_TOOLWINDOW
style = style | WS_EX_APPWINDOW

ctypes.windll.user32.SetWindowLongW(
    hwnd,
    GWL_EXSTYLE,
    style
)

root.withdraw()
root.after(10, root.deiconify)
apply_window_shape()

root.mainloop()