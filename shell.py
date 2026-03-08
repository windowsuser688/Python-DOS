try:
    import curses
except ImportError:
    print("ERROR: curses library not found!")
    print("Please install it with: pip install windows-curses")
    input("Press Enter to exit...")
    exit(1)

import subprocess

def load_config():
    """Load configuration from config.json"""
    import json
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except:
        return {
            "timezone": "UTC",
            "scaling": 1.0,
            "background_color": "blue",
            "selection_color": "red"
        }

def get_color_code(color_name):
    """Convert color name to curses color code"""
    color_map = {
        "black": curses.COLOR_BLACK,
        "red": curses.COLOR_RED,
        "green": curses.COLOR_GREEN,
        "yellow": curses.COLOR_YELLOW,
        "blue": curses.COLOR_BLUE,
        "magenta": curses.COLOR_MAGENTA,
        "cyan": curses.COLOR_CYAN,
        "white": curses.COLOR_WHITE
    }
    return color_map.get(color_name.lower(), curses.COLOR_BLUE)

def draw_window(stdscr, y, x, w, h, title, lines, selected=None):
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
    
    # Draw scrollbar if needed
    if len(lines) > h-2:
        scrollbar_height = h - 2
        thumb_size = max(1, int((h-2) / len(lines) * scrollbar_height))
        thumb_pos = int((selected or 0) / len(lines) * scrollbar_height) if selected is not None else 0
        
        for i in range(scrollbar_height):
            if thumb_pos <= i < thumb_pos + thumb_size:
                stdscr.addstr(y+1+i, x+w-2, "█", curses.color_pair(2))
            else:
                stdscr.addstr(y+1+i, x+w-2, "░", curses.color_pair(2))
    
    # Draw shadow
    stdscr.attron(curses.color_pair(4))
    for i in range(h):
        stdscr.addstr(y+i, x+w, " ")
    stdscr.addstr(y+h, x+1, " " * w)
    stdscr.attroff(curses.color_pair(4))

def validate_user_folders():
    """Validate and clean up user folders in usr/ directory"""
    import os
    import shutil
    
    try:
        # Load config to get valid users
        config = load_config()
        valid_users = [user['username'] for user in config.get('users', [])]
        users_list = config.get('users', [])
        config_modified = False
        
        # Check if usr directory exists
        if not os.path.exists('usr'):
            os.makedirs('usr')
        
        # Ensure root user exists
        has_root = any(user['username'] == 'root' for user in users_list)
        if not has_root:
            # Create root user
            users_list.append({
                'username': 'root',
                'password': '',
                'home_dir': 'usr/root'
            })
            config_modified = True
            # Create root directories
            os.makedirs('usr/root/Documents', exist_ok=True)
            os.makedirs('usr/root/Downloads', exist_ok=True)
        
        # Check if root folder exists
        if not os.path.exists('usr/root'):
            os.makedirs('usr/root/Documents', exist_ok=True)
            os.makedirs('usr/root/Downloads', exist_ok=True)
        
        # Get all folders in usr/
        usr_folders = [f for f in os.listdir('usr') if os.path.isdir(os.path.join('usr', f))]
        
        # Remove users from config if their folder doesn't exist
        users_to_remove = []
        for user in users_list:
            username = user['username']
            if username not in usr_folders and username != 'root':
                users_to_remove.append(user)
        
        if users_to_remove:
            for user in users_to_remove:
                users_list.remove(user)
            config_modified = True
        
        # Check folders in usr/
        for folder in usr_folders:
            folder_path = os.path.join('usr', folder)
            
            # Check if this folder corresponds to a valid user
            if folder not in valid_users:
                # Check if it has Documents and Downloads subdirectories
                has_documents = os.path.exists(os.path.join(folder_path, 'Documents'))
                has_downloads = os.path.exists(os.path.join(folder_path, 'Downloads'))
                
                if has_documents and has_downloads:
                    # Valid structure - add as a user to config
                    users_list.append({
                        'username': folder,
                        'password': '',
                        'home_dir': f'usr/{folder}'
                    })
                    config_modified = True
                else:
                    # Invalid user folder - delete it (unless it's root)
                    if folder != 'root':
                        try:
                            shutil.rmtree(folder_path)
                        except:
                            pass
        
        # Save config if we made changes
        if config_modified:
            config['users'] = users_list
            # Ensure current_user is valid
            current_user = config.get('current_user', 'root')
            if current_user not in [u['username'] for u in users_list]:
                config['current_user'] = 'root'
            save_config(config)
    except:
        pass

def boot_sequence(stdscr):
    """Show fake GRUB bootloader and boot messages"""
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)  # boot text
    curses.init_pair(7, curses.COLOR_GREEN, curses.COLOR_BLACK)  # OK text
    
    stdscr.clear()
    stdscr.bkgd(" ", curses.color_pair(6))
    
    boot_messages = [
        "GRUB loading...",
        "Loading Python-DOS...",
        "",
        "Starting system services...",
        "[ OK ] Started System Logging Service",
        "[ OK ] Started Network Manager",
        "[ OK ] Started User Manager",
        "[ OK ] Started File System Check",
        "[ OK ] Mounted /dev/sda1",
        "[ OK ] Started Terminal Service",
        "[ OK ] Started Display Manager",
        "[ OK ] Started Audio Service",
        "[ OK ] Reached target Multi-User System",
        "",
        "Python-DOS 1.0.0 (tty1)",
        "",
        "Starting environment...",
    ]
    
    import time
    y = 2
    
    for msg in boot_messages:
        if "[ OK ]" in msg:
            # Split the message to color only "OK"
            parts = msg.split("OK")
            stdscr.addstr(y, 2, parts[0], curses.color_pair(6))
            stdscr.addstr(y, 2 + len(parts[0]), "OK", curses.color_pair(7))
            stdscr.addstr(y, 2 + len(parts[0]) + 2, parts[1], curses.color_pair(6))
        else:
            stdscr.addstr(y, 2, msg, curses.color_pair(6))
        
        stdscr.refresh()
        time.sleep(0.15)
        y += 1
    
    time.sleep(0.5)

def lock_screen(stdscr):
    """Show lock screen"""
    curses.curs_set(0)
    curses.start_color()
    
    # Load configuration
    config = load_config()
    bg_color = get_color_code(config.get('background_color', 'blue'))
    sel_color = get_color_code(config.get('selection_color', 'red'))
    
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_WHITE, sel_color)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, bg_color)
    
    stdscr.bkgd(" ", curses.color_pair(5))
    
    # Get all users
    users = config.get('users', [{'username': 'root', 'password': '', 'home_dir': 'usr/root'}])
    current_user_index = 0
    
    # Find current user index
    current_user_name = config.get('current_user', 'root')
    for i, user in enumerate(users):
        if user['username'] == current_user_name:
            current_user_index = i
            break
    
    while True:
        stdscr.clear()
        
        height, width = stdscr.getmaxyx()
        
        # Get current user info
        current_user = users[current_user_index]
        username = current_user['username']
        password = current_user.get('password', '')
        
        # Display lock screen window
        if not password:
            lines = [
                "",
                "Python-DOS",
                "",
                f"User: {username}",
                "",
                "Press ENTER to login",
                "",
                f"TAB: Switch User ({current_user_index + 1}/{len(users)})",
                "ESC: Shutdown"
            ]
        else:
            lines = [
                "",
                "Python-DOS",
                "",
                f"User: {username}",
                "",
                "Password required",
                "",
                "Press ENTER to login",
                "",
                f"TAB: Switch User ({current_user_index + 1}/{len(users)})",
                "ESC: Shutdown"
            ]
        
        win_height = len(lines) + 4
        win_width = 40
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        draw_window(stdscr, win_y, win_x, win_width, win_height, "Login", lines)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 9:  # TAB - Switch user
            current_user_index = (current_user_index + 1) % len(users)
        
        elif key in [10, 13]:  # ENTER
            if not password:
                # No password - login directly
                config['current_user'] = username
                save_config(config)
                return True
            else:
                # Password required
                entered_password = get_password_input(stdscr, username)
                if entered_password is None:  # ESC pressed
                    continue
                elif entered_password == password:
                    # Correct password - update current user and login
                    config['current_user'] = username
                    save_config(config)
                    return True
                else:
                    # Show error
                    stdscr.clear()
                    error_lines = [
                        "",
                        "Incorrect password!",
                        "",
                        "Press any key to try again"
                    ]
                    draw_window(stdscr, win_y, win_x, win_width, 8, "Error", error_lines)
                    stdscr.refresh()
                    stdscr.getch()
        
        elif key == 27:  # ESC
            return False

def save_config(config):
    """Save configuration to config.json"""
    import json
    try:
        with open('config.json', 'w') as f:
            json.dump(config, indent=4, fp=f)
    except:
        pass

def get_password_input(stdscr, username):
    """Get password input from user"""
    curses.curs_set(1)
    password = ""
    
    height, width = stdscr.getmaxyx()
    
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        # Show password input window
        lines = [
            "",
            f"User: {username}",
            "",
            "Enter Password:",
            "",
            "*" * len(password),
            "",
            "ENTER: Submit | ESC: Cancel"
        ]
        
        win_height = len(lines) + 4
        win_width = 40
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        draw_window(stdscr, win_y, win_x, win_width, win_height, "Password", lines)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            curses.curs_set(0)
            return None
        elif key in [10, 13]:  # ENTER
            curses.curs_set(0)
            return password
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            if password:
                password = password[:-1]
        elif 32 <= key <= 126:
            password += chr(key)

def desktop(stdscr):
    curses.curs_set(0)
    curses.start_color()
    
    # Load configuration
    config = load_config()
    bg_color = get_color_code(config.get('background_color', 'blue'))
    sel_color = get_color_code(config.get('selection_color', 'red'))
    
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)   # window fill
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)   # borders
    curses.init_pair(3, curses.COLOR_WHITE, sel_color)            # selection (configurable)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)   # shadow
    curses.init_pair(5, curses.COLOR_WHITE, bg_color)             # desktop bg (configurable)
    
    stdscr.bkgd(" ", curses.color_pair(5))
    
    menu = ["File Explorer", "Terminal", "Calculator", "Notepad", "Python IDE", "Music Player", "Web Browser", "Settings", "Log Out", "Restart", "Bootloader", "Shutdown"]
    selected = 0
    
    while True:
        stdscr.clear()
        draw_window(stdscr, 5, 10, 35, len(menu)+4, "Main Menu", menu, selected)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(menu)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(menu)
        elif key in [10, 13]:
            choice = menu[selected]
            
            if choice == "File Explorer":
                curses.endwin()
                subprocess.run(["python", "apps/file_explorer.py"])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
            
            elif choice == "Terminal":
                curses.endwin()
                subprocess.run(["python", "apps/terminal.py"])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
            
            elif choice == "Calculator":
                curses.endwin()
                subprocess.run(["python", "apps/calculator.py"])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
            
            elif choice == "Notepad":
                curses.endwin()
                subprocess.run(["python", "apps/notepad.py"])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
            
            elif choice == "Python IDE":
                curses.endwin()
                subprocess.run(["python", "apps/python_ide.py"])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
            
            elif choice == "Music Player":
                curses.endwin()
                subprocess.run(["python", "apps/music_player.py"])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
            
            elif choice == "Web Browser":
                curses.endwin()
                subprocess.run(["python", "apps/web_browser.py"])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
            
            elif choice == "Settings":
                curses.endwin()
                subprocess.run(["python", "apps/settings.py"])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
            
            elif choice == "Log Out":
                stdscr.clear()
                stdscr.bkgd(" ", curses.color_pair(5))
                draw_window(stdscr, 5, 10, 35, 5, "Logging Out", ["Logging out..."])
                stdscr.refresh()
                import time
                time.sleep(1)
                return "logout"
            
            elif choice == "Restart":
                stdscr.clear()
                stdscr.bkgd(" ", curses.color_pair(5))
                draw_window(stdscr, 5, 10, 35, 5, "Restarting", ["System restarting..."])
                stdscr.refresh()
                import time
                time.sleep(1)
                # Show boot sequence
                boot_sequence(stdscr)
                # Reinitialize colors for desktop
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                # Reset selection
                selected = 0
            
            elif choice == "Bootloader":
                stdscr.clear()
                stdscr.bkgd(" ", curses.color_pair(5))
                draw_window(stdscr, 5, 10, 35, 5, "Rebooting", ["Returning to bootloader..."])
                stdscr.refresh()
                import time
                time.sleep(1)
                # Exit to bootloader
                curses.endwin()
                subprocess.run(["python", "bootloader/bootloader.py"])
                # When bootloader exits, we're done
                return "bootloader"
            
            elif choice == "Shutdown":
                stdscr.clear()
                draw_window(stdscr, 5, 10, 35, 5, "Shutdown", ["System shutting down..."])
                stdscr.refresh()
                stdscr.getch()
                break

def main(stdscr):
    # Validate user folders before boot
    validate_user_folders()
    
    # Show boot sequence only once at startup
    boot_sequence(stdscr)
    
    while True:
        # Show lock screen
        if not lock_screen(stdscr):
            # User pressed ESC on lock screen - shutdown
            break
        
        # User logged in - show desktop
        result = desktop(stdscr)
        
        # If desktop returns "logout", go back to lock screen (no reboot)
        # If desktop returns "bootloader", exit to bootloader
        # If desktop returns None or anything else, exit completely
        if result == "logout":
            continue  # Go back to lock screen
        elif result == "bootloader":
            break  # Exit to bootloader
        else:
            break  # Shutdown

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Failed to start: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
