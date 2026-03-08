try:
    import curses
except ImportError:
    print("ERROR: curses library not found!")
    print("Please install it with: pip install windows-curses")
    input("Press Enter to exit...")
    exit(1)

import subprocess
import time

def verbose_boot(stdscr):
    """Show verbose boot sequence with detailed messages"""
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)   # normal text
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # OK text
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # INFO text
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)    # DEBUG text
    
    stdscr.bkgd(" ", curses.color_pair(1))
    stdscr.clear()
    
    verbose_messages = [
        ("INFO", "Python-DOS Bootloader v1.0"),
        ("INFO", "Verbose mode enabled"),
        ("DEBUG", "Initializing system..."),
        ("", ""),
        ("DEBUG", "Loading BIOS..."),
        ("OK", "BIOS loaded successfully"),
        ("DEBUG", "Detecting hardware..."),
        ("INFO", "CPU: Python Virtual Processor"),
        ("INFO", "RAM: Unlimited"),
        ("INFO", "Display: Terminal Console"),
        ("OK", "Hardware detection complete"),
        ("", ""),
        ("DEBUG", "Loading bootloader..."),
        ("OK", "Bootloader loaded at 0x0000"),
        ("DEBUG", "Searching for boot device..."),
        ("INFO", "Found boot device: /dev/python0"),
        ("OK", "Boot device mounted"),
        ("", ""),
        ("DEBUG", "Loading kernel modules..."),
        ("INFO", "Loading module: curses.ko"),
        ("OK", "Module curses.ko loaded"),
        ("INFO", "Loading module: subprocess.ko"),
        ("OK", "Module subprocess.ko loaded"),
        ("INFO", "Loading module: json.ko"),
        ("OK", "Module json.ko loaded"),
        ("", ""),
        ("DEBUG", "Initializing file systems..."),
        ("INFO", "Mounting /usr/root/Documents"),
        ("OK", "Mounted /usr/root/Documents"),
        ("INFO", "Mounting /usr/root/Downloads"),
        ("OK", "Mounted /usr/root/Downloads"),
        ("INFO", "Mounting /apps"),
        ("OK", "Mounted /apps"),
        ("", ""),
        ("DEBUG", "Starting system services..."),
        ("INFO", "Starting System Logging Service"),
        ("OK", "Started System Logging Service"),
        ("INFO", "Starting Network Manager"),
        ("OK", "Started Network Manager"),
        ("INFO", "Starting User Manager"),
        ("OK", "Started User Manager"),
        ("INFO", "Starting File System Check"),
        ("OK", "Started File System Check"),
        ("INFO", "Starting Terminal Service"),
        ("OK", "Started Terminal Service"),
        ("INFO", "Starting Display Manager"),
        ("OK", "Started Display Manager"),
        ("INFO", "Starting Audio Service"),
        ("OK", "Started Audio Service"),
        ("", ""),
        ("DEBUG", "Loading configuration..."),
        ("INFO", "Reading config.json"),
        ("OK", "Configuration loaded"),
        ("INFO", "Region: United States"),
        ("INFO", "Background: blue"),
        ("INFO", "Selection: red"),
        ("", ""),
        ("DEBUG", "Initializing desktop environment..."),
        ("INFO", "Loading color schemes"),
        ("OK", "Color schemes loaded"),
        ("INFO", "Initializing window manager"),
        ("OK", "Window manager initialized"),
        ("INFO", "Loading applications"),
        ("OK", "Applications loaded"),
        ("", ""),
        ("OK", "Reached target Multi-User System"),
        ("INFO", "Python-DOS 1.0.0 (tty1)"),
        ("", ""),
        ("INFO", "localhost login: root"),
        ("INFO", "Password: ********"),
        ("OK", "Login successful"),
        ("", ""),
        ("INFO", "Starting desktop environment..."),
        ("DEBUG", "Launching Python-DOS..."),
    ]
    
    y = 1
    max_y, max_x = stdscr.getmaxyx()
    
    for msg_type, message in verbose_messages:
        if y >= max_y - 2:
            # Scroll up
            stdscr.clear()
            y = 1
        
        if msg_type == "OK":
            stdscr.addstr(y, 2, "[  OK  ] ", curses.color_pair(2))
            stdscr.addstr(y, 12, message, curses.color_pair(1))
        elif msg_type == "INFO":
            stdscr.addstr(y, 2, "[ INFO ] ", curses.color_pair(3))
            stdscr.addstr(y, 12, message, curses.color_pair(1))
        elif msg_type == "DEBUG":
            stdscr.addstr(y, 2, "[DEBUG ] ", curses.color_pair(4))
            stdscr.addstr(y, 12, message, curses.color_pair(1))
        else:
            stdscr.addstr(y, 2, message, curses.color_pair(1))
        
        stdscr.refresh()
        time.sleep(0.08)  # Slower for readability
        y += 1
    
    # Final message
    stdscr.addstr(y + 1, 2, "Press any key to continue...", curses.color_pair(3))
    stdscr.refresh()
    stdscr.timeout(-1)
    stdscr.getch()
    
    # Launch the OS
    curses.endwin()
    subprocess.run(["python", "shell.py"])

def main(stdscr):
    verbose_boot(stdscr)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Failed to start verbose mode: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
