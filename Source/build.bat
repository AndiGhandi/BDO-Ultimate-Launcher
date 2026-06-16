@echo off
title BDO Ultimate Launcher Builder

echo Installing dependencies...

py -m pip install --upgrade pip
py -m pip install customtkinter pillow pyinstaller pywin32

echo.
echo Building launcher...

py -m PyInstaller ^
--onefile ^
--windowed ^
--icon=BDOStart.ico ^
--add-data "background.png;." ^
--add-data "BDOStart.ico;." ^
--add-data "smooth_off.nip;." ^
--add-data "smooth_on.nip;." ^
--add-data "SEMIPOTATO.nip;." ^
--add-data "GIGAPOTATO.nip;." ^
--add-data "nvidiaProfileInspector.exe;." ^
BDO_Launcher.py

echo.
echo Build finished.
pause