# Python-DOS

A graphical OS simulator that runs in your terminal with a classic blue interface.

## Features

- Main Menu with navigation
- Shutdown/Restart options with boot sequence
- File Explorer
- Terminal
- Calculator app
- Notepad text editor
- Music Player
- Web Browser
- Settings with customizable colors and regions
- Classic blue GUI look with shadows

## How to Run

```bash
python shell.py
```

Or use the batch file (Windows):
```bash
run.bat
```

Or start from bootloader:
```bash
python bootloader/bootloader.py
```

## Controls

- **Arrow Keys (↑/↓)**: Navigate menu items
- **Enter**: Select menu item
- **ESC**: Go back to main menu / Exit apps
- **Ctrl+C**: Force quit

## Requirements

- Python 3.x
- curses library (built-in on Linux/Mac, use `windows-curses` on Windows)
- pygame (optional, for Music Player)

### Windows Installation

```bash
pip install windows-curses
pip install pygame
```

## Apps

- **File Explorer**: Browse files and directories
- **Terminal**: Execute commands
- **Calculator**: Basic arithmetic operations
- **Notepad**: Text editor with save/load
- **Music Player**: Play MP3/WAV/OGG files
- **Web Browser**: Browse websites (text-only)
- **Settings**: Customize colors, region, and scaling

