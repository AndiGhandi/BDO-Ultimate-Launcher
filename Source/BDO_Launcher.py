"""
BDO Ultimate Launcher
Created by AndiGhandi https://github.com/AndiGhandi

GitHub:
https://github.com/AndiGhandi/BDO-Ultimate-Launcher

License:
MIT License with Attribution Requirement
"""

import os
import sys
import ctypes
import subprocess
import webbrowser
import shutil

import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

CONFIG_FILE = "config.ini"
VERSION = "1.0.2"

LAUNCHER_GITHUB_URL = "https://github.com/AndiGhandi/BDO-Ultimate-Launcher"
NPI_GITHUB_URL = "https://github.com/Orbmu2k/nvidiaProfileInspector"
AFFINITY_GUIDE_URL = "https://docs.google.com/document/d/1cyLaDiPL_B6nOZw_qPE_wOGuoeRT-qddTjevTFoFBkg/view?tab=t.0#heading=h.rl325eap4pk9"

# Used as CustomTkinter background color behind rounded UI corners.
# This prevents gray corner artifacts while matching the artwork reasonably well.
PANEL_CORNER_BG = "#0A0D11"

APP_FOLDER = os.path.join(
    os.environ["APPDATA"],
    "BDO Ultimate Launcher"
)

PROFILE_FOLDER = os.path.join(
    APP_FOLDER,
    "Profiles"
)

os.makedirs(APP_FOLDER, exist_ok=True)
os.makedirs(PROFILE_FOLDER, exist_ok=True)

CONFIG_PATH = os.path.join(
    APP_FOLDER,
    CONFIG_FILE
)

BUILTIN_PROFILES = [
    "smooth_off.nip",
    "smooth_on.nip",
    "SEMIPOTATO.nip",
    "GIGAPOTATO.nip"
]


# =====================================
# BASE DIRECTORY / RESOURCE HANDLING
# =====================================

if getattr(sys, "frozen", False):
    BASEDIR = os.path.dirname(sys.executable)
else:
    BASEDIR = os.path.dirname(os.path.abspath(__file__))


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = BASEDIR

    return os.path.join(base_path, relative_path)


def install_builtin_profiles():
    """
    Copies the bundled default profiles from the EXE/source folder to:
    %APPDATA%\\BDO Ultimate Launcher\\Profiles

    Existing user-modified files are not overwritten.
    """
    for profile in BUILTIN_PROFILES:
        source = resource_path(profile)
        target = os.path.join(PROFILE_FOLDER, profile)

        if os.path.exists(source) and not os.path.exists(target):
            try:
                shutil.copy2(source, target)
            except Exception as e:
                messagebox.showwarning(
                    "Profile Install Warning",
                    f"Could not install default profile:\n{profile}\n\n{e}"
                )


# =====================================
# ADMIN ELEVATION
# =====================================

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
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

    except Exception:
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

    except Exception:
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
        f.write(f"SHOW_POTATO_POPUP={int(show_potato_popup_var.get())}\n")

    messagebox.showinfo(
        "Success",
        "Configuration saved successfully!"
    )


def create_default_config():
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write("GAMEPATH=\n")
        f.write("AFFINITY=555\n")
        f.write("USE_STEAM=1\n")
        f.write("PROFILE=smooth_off.nip\n")
        f.write("USE_NVIDIA=1\n")
        f.write("USE_AFFINITY=1\n")
        f.write("SHOW_POTATO_POPUP=1\n")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        create_default_config()

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
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

            elif key == "SHOW_POTATO_POPUP":
                show_potato_popup_var.set(value == "1")

            elif key == "PROFILE":
                # Only set it if the profile exists; otherwise keep default.
                if value in detect_profiles():
                    profile_var.set(value)


# =====================================
# PROFILE HANDLING
# =====================================

def detect_profiles():
    profiles = []

    if os.path.exists(PROFILE_FOLDER):
        for file in os.listdir(PROFILE_FOLDER):
            if file.lower().endswith(".nip"):
                profiles.append(file)

    profiles.sort(key=lambda x: x.lower())
    return profiles


def refresh_profiles():
    new_profiles = detect_profiles()

    if not new_profiles:
        new_profiles = ["No .nip files found"]

    profile_dropdown.configure(values=new_profiles)

    if profile_var.get() not in new_profiles:
        default_profile = "smooth_off.nip"

        if default_profile in new_profiles:
            profile_var.set(default_profile)
        else:
            profile_var.set(new_profiles[0])


def get_profile_signature():
    """
    Returns a lightweight snapshot of the Profiles folder.
    This lets the launcher detect newly added / edited .nip files while running.
    """
    signature = []

    if os.path.exists(PROFILE_FOLDER):
        for file in os.listdir(PROFILE_FOLDER):
            if file.lower().endswith(".nip"):
                path = os.path.join(PROFILE_FOLDER, file)

                try:
                    stat = os.stat(path)
                    signature.append((file.lower(), stat.st_mtime, stat.st_size))

                except OSError:
                    signature.append((file.lower(), 0, 0))

    return tuple(sorted(signature))


_last_profile_signature = None


def auto_refresh_profiles():
    """
    Automatically refreshes the profile dropdown if .nip files are added,
    removed, or modified in %APPDATA%\BDO Ultimate Launcher\Profiles.
    """
    global _last_profile_signature

    current_signature = get_profile_signature()

    if current_signature != _last_profile_signature:
        _last_profile_signature = current_signature
        refresh_profiles()

    root.after(2000, auto_refresh_profiles)


def open_profile_folder():
    os.makedirs(PROFILE_FOLDER, exist_ok=True)
    os.startfile(PROFILE_FOLDER)


def open_profile_inspector():
    inspector = resource_path("nvidiaProfileInspector.exe")

    if not os.path.exists(inspector):
        messagebox.showerror(
            "Error",
            "nvidiaProfileInspector.exe not found!"
        )
        return

    os.makedirs(PROFILE_FOLDER, exist_ok=True)
    os.startfile(PROFILE_FOLDER)

    try:
        proc = subprocess.Popen([inspector])
        root.after(1000, lambda: check_profile_inspector_closed(proc))

    except Exception as e:
        messagebox.showerror(
            "Error",
            f"Could not open NVIDIA Profile Inspector:\n\n{e}"
        )


def check_profile_inspector_closed(proc):
    if proc.poll() is None:
        root.after(1000, lambda: check_profile_inspector_closed(proc))
    else:
        refresh_profiles()


def on_profile_change(selected_profile):
    profile_var.set(selected_profile)

    if (
        show_potato_popup_var.get()
        and selected_profile.upper() in ["SEMIPOTATO.NIP", "GIGAPOTATO.NIP"]
    ):
        messagebox.showinfo(
            "Recommended BDO Settings",
            "For SEMIPOTATO / GIGAPOTATO profiles:\n\n"
            "- Texture Quality: High\n"
            "- Graphics: Lowest / Optimal\n"
            "- Effect Opacity: Minimum value (30)\n\n"
            "These profiles work best with reduced in-game effects."
        )


# =====================================
# BROWSE
# =====================================

def browse_gamepath():
    path = filedialog.askdirectory()

    if path:
        gamepath_var.set(path)


# =====================================
# LINKS
# =====================================

def open_affinity_guide():
    webbrowser.open(AFFINITY_GUIDE_URL)


def open_profile_inspector_github():
    webbrowser.open(NPI_GITHUB_URL)


def open_launcher_github():
    webbrowser.open(LAUNCHER_GITHUB_URL)


# =====================================
# LAUNCH
# =====================================

def launch_game():
    profile = profile_var.get()

    inspector = resource_path(
        "nvidiaProfileInspector.exe"
    )

    profile_file = os.path.join(
        PROFILE_FOLDER,
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
                f"Profile not found:\n{profile_file}"
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
root.configure(fg_color=PANEL_CORNER_BG)

myappid = "BDOUltimateLauncher.1.0"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

root.geometry("1024x1024")
root.resizable(True, True)
root.minsize(900, 900)
root.maxsize(1024, 1024)

root.overrideredirect(True)

# Icon
ico = resource_path("BDOStart.ico")

if os.path.exists(ico):
    try:
        root.iconbitmap(ico)
    except Exception:
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


root.bind("<Escape>", lambda e: root.destroy())


# =====================================
# BACKGROUND IMAGE
# =====================================

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
    height=590,
    corner_radius=25,
    fg_color="#080808",
    bg_color=PANEL_CORNER_BG
)

# Moved the UI panel upward so the BDO Launcher text in the background remains visible.
left_panel.place(x=80, y=100)


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

gpu_label.place(x=10, y=12)


# =====================================
# DIRECTORY
# =====================================

dir_label = ctk.CTkLabel(
    left_panel,
    text=f"Config Directory\n{APP_FOLDER}",
    justify="left",
    wraplength=220,
    font=("Segoe UI", 13, "bold"),
    text_color="#D4AF37"
)

dir_label.place(x=10, y=102)


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

gamepath_label.place(x=10, y=160)

gamepath_entry = ctk.CTkEntry(
    left_panel,
    width=220,
    textvariable=gamepath_var
)

gamepath_entry.place(x=10, y=187)

browse_btn = ctk.CTkButton(
    left_panel,
    text="Browse",
    width=100,
    height=26,
    command=browse_gamepath
)

browse_btn.place(x=10, y=222)


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

affinity_label.place(x=10, y=252)

affinity_entry = ctk.CTkEntry(
    left_panel,
    width=70,
    textvariable=affinity_var
)

affinity_entry.place(x=10, y=280)

affinity_enabled_var = ctk.BooleanVar(value=True)

affinity_checkbox = ctk.CTkCheckBox(
    left_panel,
    text="Use CPU Affinity",
    variable=affinity_enabled_var
)

affinity_checkbox.place(x=95, y=280)

guide = ctk.CTkLabel(
    left_panel,
    text="CPU Affinity Guide",
    text_color="#55AAFF",
    cursor="hand2"
)

guide.place(x=10, y=315)

guide.bind(
    "<Button-1>",
    lambda e: open_affinity_guide()
)


# =====================================
# VARIABLES
# =====================================

steam_var = ctk.BooleanVar(value=True)
nvidia_var = ctk.BooleanVar(value=True)
show_potato_popup_var = ctk.BooleanVar(value=True)


# =====================================
# STEAM / NVIDIA
# =====================================

steam_checkbox = ctk.CTkCheckBox(
    left_panel,
    text="Launch via Steam",
    variable=steam_var
)

steam_checkbox.place(x=10, y=345)

nvidia_checkbox = ctk.CTkCheckBox(
    left_panel,
    text="Use NVIDIA Profile Inspector",
    variable=nvidia_var
)

nvidia_checkbox.place(x=10, y=375)

if not HAS_NVIDIA:
    nvidia_var.set(False)
    nvidia_checkbox.configure(state="disabled")


# =====================================
# PROFILES
# =====================================

install_builtin_profiles()

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

profile_label.place(x=10, y=405)

profile_dropdown = ctk.CTkOptionMenu(
    left_panel,
    values=profiles,
    variable=profile_var,
    width=220,
    command=on_profile_change
)

profile_dropdown.place(x=10, y=430)

show_potato_popup_checkbox = ctk.CTkCheckBox(
    left_panel,
    text="Show Potato Popup",
    variable=show_potato_popup_var
)

show_potato_popup_checkbox.place(x=10, y=462)

custom_profile_btn = ctk.CTkButton(
    left_panel,
    text="Create / Edit Custom Profiles",
    width=220,
    height=26,
    command=open_profile_inspector
)

custom_profile_btn.place(x=10, y=492)

open_profiles_btn = ctk.CTkButton(
    left_panel,
    text="Open Profiles Folder",
    width=220,
    height=26,
    command=open_profile_folder
)

open_profiles_btn.place(x=10, y=522)


# =====================================
# SAVE
# =====================================

save_btn = ctk.CTkButton(
    left_panel,
    text="Save Configuration",
    width=220,
    height=26,
    command=save_config
)

save_btn.place(x=10, y=552)


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

launch_btn.place(x=530, y=825)


# =====================================
# FOOTER / LINKS
# =====================================

footer = ctk.CTkLabel(
    root,
    text=f"BDO Ultimate Launcher v{VERSION} by Ghandi",
    text_color="#AAAAAA",
    font=("Segoe UI", 12),
    cursor="hand2"
)

footer.place(x=610, y=963)

footer.bind(
    "<Button-1>",
    lambda e: open_launcher_github()
)

npi_footer_link = ctk.CTkLabel(
    root,
    text="NVIDIA Profile Inspector",
    text_color="#55AAFF",
    font=("Segoe UI", 11),
    cursor="hand2"
)

# Placed below the BDO Launcher text on the background.
npi_footer_link.place(x=190, y=963)

npi_footer_link.bind(
    "<Button-1>",
    lambda e: open_profile_inspector_github()
)


# =====================================
# WINDOW SHAPE
# =====================================

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
refresh_profiles()
_last_profile_signature = get_profile_signature()
root.after(2000, auto_refresh_profiles)

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
