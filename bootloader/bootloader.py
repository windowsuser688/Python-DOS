try:
    import curses
except ImportError:
    print("ERROR: curses library not found!")
    print("Please install it with: pip install windows-curses")
    input("Press Enter to exit...")
    exit(1)

import subprocess
import time

def draw_window(stdscr, y, x, w, h, title, lines, selected=None):
    """Draw a window with border, title, and shadow"""
    # Fill window background
    for i in range(h):
        stdscr.addstr(y+i, x, " " * w, curses.color_pair(1))
    
    # Draw borders
    stdscr.attron(curses.color_pair(2))
    stdscr.addstr(y, x, "┌" + "─"*(w-2) + "┐")
    for i in range(1, h-1):
        stdscr.addstr(y+i, x, "│" + " "*(w-2) + "│")
    stdscr.addstr(y+h-1, x, "└" + "─"*(w-2) + "┘")
    stdscr.attroff(curses.color_pair(2))
    
    # Draw title
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(y, x+2, f" {title} ")
    stdscr.attroff(curses.color_pair(1))
    
    # Draw content
    for i, line in enumerate(lines):
        if i < h-2:
            if selected is not None and i == selected:
                stdscr.addstr(y+1+i, x+2, line, curses.color_pair(3))
            else:
                stdscr.addstr(y+1+i, x+2, line, curses.color_pair(1))
    
    # Draw shadow
    stdscr.attron(curses.color_pair(4))
    for i in range(h):
        try:
            stdscr.addstr(y+i, x+w, " ")
        except:
            pass
    try:
        stdscr.addstr(y+h, x+1, " " * w)
    except:
        pass
    stdscr.attroff(curses.color_pair(4))

def bootloader(stdscr):
    curses.curs_set(0)
    curses.start_color()
    
    # Colors for bootloader (white on black background)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)   # window fill
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)   # borders
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)   # selection (inverted)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)   # shadow
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)   # title
    
    stdscr.bkgd(" ", curses.color_pair(1))
    
    menu = ["Boot Python-DOS", "Boot Options", "System Information", "Exit to BIOS"]
    selected = 0
    countdown = 5
    auto_boot = True
    
    stdscr.timeout(1000)  # 1 second timeout for getch
    
    while True:
        stdscr.clear()
        
        height, width = stdscr.getmaxyx()
        
        # Draw title
        title = "Python-DOS Bootloader v1.0"
        stdscr.addstr(2, (width - len(title)) // 2, title, curses.color_pair(5) | curses.A_BOLD)
        
        # Draw menu
        menu_lines = []
        for item in menu:
            menu_lines.append(item)
        
        if auto_boot and countdown > 0:
            menu_lines.append("")
            menu_lines.append(f"Auto-booting in {countdown} seconds...")
            menu_lines.append("Press any key to stop")
        
        win_height = len(menu_lines) + 4
        win_width = 45
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        draw_window(stdscr, win_y, win_x, win_width, win_height, "Boot Menu", menu_lines, selected)
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == -1:  # Timeout (1 second passed)
            if auto_boot and countdown > 0:
                countdown -= 1
                if countdown == 0:
                    # Auto-boot Python-DOS
                    boot_os(stdscr)
                    return
        elif key == curses.KEY_UP:
            auto_boot = False
            selected = (selected - 1) % len(menu)
        elif key == curses.KEY_DOWN:
            auto_boot = False
            selected = (selected + 1) % len(menu)
        elif key in [10, 13]:  # ENTER
            auto_boot = False
            choice = menu[selected]
            
            if choice == "Boot Python-DOS":
                boot_os(stdscr)
                return
            
            elif choice == "Boot Options":
                boot_option = show_boot_options(stdscr)
                if boot_option == "safe_mode":
                    boot_safe_mode(stdscr)
                    return
                elif boot_option == "verbose_mode":
                    boot_verbose_mode(stdscr)
                    return
                elif boot_option == "single_user_mode":
                    boot_single_user_mode(stdscr)
                    return
            
            elif choice == "System Information":
                show_system_info(stdscr)
            
            elif choice == "Exit to BIOS":
                show_exit_message(stdscr)
                return
        else:
            # Any other key stops auto-boot
            auto_boot = False

def boot_os(stdscr):
    """Boot the operating system"""
    stdscr.clear()
    stdscr.bkgd(" ", curses.color_pair(1))
    
    height, width = stdscr.getmaxyx()
    
    msg = "Booting Python-DOS..."
    stdscr.addstr(height // 2, (width - len(msg)) // 2, msg, curses.color_pair(5))
    stdscr.refresh()
    time.sleep(1)
    
    # Launch the OS
    curses.endwin()
    subprocess.run(["python", "shell.py"])

def boot_safe_mode(stdscr):
    """Boot into safe mode"""
    stdscr.clear()
    stdscr.bkgd(" ", curses.color_pair(1))
    
    height, width = stdscr.getmaxyx()
    
    msg = "Booting Python-DOS in Safe Mode..."
    stdscr.addstr(height // 2, (width - len(msg)) // 2, msg, curses.color_pair(5))
    stdscr.refresh()
    time.sleep(1)
    
    # Launch safe mode
    curses.endwin()
    subprocess.run(["python", "safemode/safemode.py"])

def boot_verbose_mode(stdscr):
    """Boot into verbose mode"""
    stdscr.clear()
    stdscr.bkgd(" ", curses.color_pair(1))
    
    height, width = stdscr.getmaxyx()
    
    msg = "Booting Python-DOS in Verbose Mode..."
    stdscr.addstr(height // 2, (width - len(msg)) // 2, msg, curses.color_pair(5))
    stdscr.refresh()
    time.sleep(1)
    
    # Launch verbose mode
    curses.endwin()
    subprocess.run(["python", "verbosemode/verbosemode.py"])

def boot_single_user_mode(stdscr):
    """Boot into single user mode"""
    stdscr.clear()
    stdscr.bkgd(" ", curses.color_pair(1))
    
    height, width = stdscr.getmaxyx()
    
    msg = "Booting Python-DOS in Single User Mode..."
    stdscr.addstr(height // 2, (width - len(msg)) // 2, msg, curses.color_pair(5))
    stdscr.refresh()
    time.sleep(1)
    
    # Launch single user mode
    curses.endwin()
    subprocess.run(["python", "singleusermode/singleusermode.py"])

def show_boot_options(stdscr):
    """Show boot options menu"""
    options = ["Safe Mode", "Verbose Boot", "Single User Mode", "Back"]
    selected = 0
    
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(1))
        
        height, width = stdscr.getmaxyx()
        
        title = "Boot Options"
        stdscr.addstr(2, (width - len(title)) // 2, title, curses.color_pair(5) | curses.A_BOLD)
        
        win_height = len(options) + 4
        win_width = 40
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        draw_window(stdscr, win_y, win_x, win_width, win_height, "Options", options, selected)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(options)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)
        elif key in [10, 13]:
            if options[selected] == "Back":
                return None
            elif options[selected] == "Safe Mode":
                return "safe_mode"
            elif options[selected] == "Verbose Boot":
                return "verbose_mode"
            elif options[selected] == "Single User Mode":
                return "single_user_mode"
            else:
                # Show "Not implemented" message
                stdscr.clear()
                msg_lines = [
                    "",
                    f"{options[selected]} is not implemented",
                    "",
                    "Press any key to continue"
                ]
                draw_window(stdscr, win_y, win_x, win_width, 8, "Notice", msg_lines)
                stdscr.refresh()
                stdscr.timeout(-1)
                stdscr.getch()
                stdscr.timeout(1000)
        elif key == 27:  # ESC
            return None

def show_system_info(stdscr):
    """Show system information"""
    stdscr.clear()
    stdscr.bkgd(" ", curses.color_pair(1))
    
    height, width = stdscr.getmaxyx()
    
    title = "System Information"
    stdscr.addstr(2, (width - len(title)) // 2, title, curses.color_pair(5) | curses.A_BOLD)
    
    info_lines = [
        "",
        "Bootloader: Python-DOS Bootloader v1.0",
        "OS: Python-DOS 1.0.0",
        "Build: 2026.03.08",
        "",
        "Platform: Python Terminal",
        "Architecture: Cross-platform",
        "",
        "Press any key to continue"
    ]
    
    win_height = len(info_lines) + 4
    win_width = 50
    win_y = (height - win_height) // 2
    win_x = (width - win_width) // 2
    
    draw_window(stdscr, win_y, win_x, win_width, win_height, "System Info", info_lines)
    stdscr.refresh()
    
    stdscr.timeout(-1)
    stdscr.getch()
    stdscr.timeout(1000)

def show_exit_message(stdscr):
    """Show exit to BIOS message"""
    stdscr.clear()
    stdscr.bkgd(" ", curses.color_pair(1))
    
    height, width = stdscr.getmaxyx()
    
    msg_lines = [
        "",
        "Exiting to BIOS...",
        "",
        "Press any key to close"
    ]
    
    win_height = len(msg_lines) + 4
    win_width = 40
    win_y = (height - win_height) // 2
    win_x = (width - win_width) // 2
    
    draw_window(stdscr, win_y, win_x, win_width, win_height, "Exit", msg_lines)
    stdscr.refresh()
    
    stdscr.timeout(-1)
    stdscr.getch()

def main(stdscr):
    bootloader(stdscr)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Failed to start bootloader: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
