try:
    import curses
except ImportError:
    print("ERROR: curses library not found!")
    print("Please install it with: pip install windows-curses")
    input("Press Enter to exit...")
    exit(1)

import sys
import os
import urllib.request
import json

# Set terminal type for simulated terminals
os.environ['TERM'] = 'xterm-256color'

sys.path.insert(0, os.path.dirname(__file__))
from config_loader import init_colors

GITHUB_API_URL = "https://api.github.com/repos/windowsuser688/Python-DOS-Apps/contents/"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/windowsuser688/Python-DOS-Apps/main/"

def draw_window(stdscr, y, x, w, h, title, lines, selected=None, scroll_offset=0):
    """Draw a window with border and shadow"""
    max_y, max_x = stdscr.getmaxyx()
    
    # Ensure window fits on screen
    if y + h >= max_y:
        h = max_y - y - 1
    if x + w >= max_x:
        w = max_x - x - 1
    
    if h < 3 or w < 3:
        return
    
    # Fill window background
    for i in range(h):
        if y + i < max_y and x < max_x:
            try:
                stdscr.addstr(y+i, x, " " * min(w, max_x - x - 1), curses.color_pair(1))
            except:
                pass
    
    # Draw borders
    try:
        stdscr.attron(curses.color_pair(2))
        if y < max_y and x + w - 1 < max_x:
            stdscr.addstr(y, x, "┌" + "─"*(w-2) + "┐")
        for i in range(1, h-1):
            if y + i < max_y:
                if x < max_x:
                    stdscr.addstr(y+i, x, "│")
                if x + w - 1 < max_x:
                    stdscr.addstr(y+i, x+w-1, "│")
        if y + h - 1 < max_y and x + w - 1 < max_x:
            stdscr.addstr(y+h-1, x, "└" + "─"*(w-2) + "┘")
        stdscr.attroff(curses.color_pair(2))
    except:
        pass
    
    # Draw title
    try:
        stdscr.attron(curses.color_pair(1))
        if y < max_y and x + 2 + len(title) + 2 < max_x:
            stdscr.addstr(y, x+2, f" {title} ")
        stdscr.attroff(curses.color_pair(1))
    except:
        pass
    
    # Draw content with scrolling
    visible_lines = h - 2
    for i in range(visible_lines):
        line_idx = scroll_offset + i
        if line_idx < len(lines) and y + 1 + i < max_y:
            line = lines[line_idx]
            display_line = line[:w-4] if len(line) > w-4 else line
            try:
                if selected is not None and line_idx == selected:
                    stdscr.addstr(y+1+i, x+2, display_line, curses.color_pair(3))
                else:
                    stdscr.addstr(y+1+i, x+2, display_line, curses.color_pair(1))
            except:
                pass
    
    # Draw scrollbar if needed
    if len(lines) > visible_lines:
        scrollbar_height = visible_lines
        thumb_size = max(1, int(visible_lines / len(lines) * scrollbar_height))
        thumb_pos = int(scroll_offset / len(lines) * scrollbar_height)
        
        try:
            for i in range(scrollbar_height):
                if y + 1 + i < max_y and x + w - 2 < max_x:
                    if thumb_pos <= i < thumb_pos + thumb_size:
                        stdscr.addstr(y+1+i, x+w-2, "█", curses.color_pair(2))
                    else:
                        stdscr.addstr(y+1+i, x+w-2, "░", curses.color_pair(2))
        except:
            pass
    
    # Draw shadow
    try:
        stdscr.attron(curses.color_pair(4))
        for i in range(h):
            if y + i < max_y and x + w < max_x:
                stdscr.addstr(y+i, x+w, " ")
        if y + h < max_y and x + 1 + w < max_x:
            stdscr.addstr(y+h, x+1, " " * min(w, max_x - x - 1))
        stdscr.attroff(curses.color_pair(4))
    except:
        pass

def show_message(stdscr, message):
    """Show a message dialog"""
    stdscr.clear()
    stdscr.bkgd(" ", curses.color_pair(5))
    
    # Split message into lines
    message_lines = message.split('\n')
    
    lines = [""]
    lines.extend(message_lines)
    lines.extend(["", "Press any key to continue"])
    
    height, width = stdscr.getmaxyx()
    win_height = len(lines) + 4
    win_width = max(50, max(len(line) for line in lines) + 6)
    win_y = (height - win_height) // 2
    win_x = (width - win_width) // 2
    
    draw_window(stdscr, win_y, win_x, win_width, win_height, "Message", lines)
    stdscr.refresh()
    stdscr.getch()

def fetch_available_apps():
    """Fetch list of available apps from GitHub"""
    try:
        with urllib.request.urlopen(GITHUB_API_URL) as response:
            data = json.loads(response.read().decode())
            # Filter only .py files
            apps = [item for item in data if item['name'].endswith('.py')]
            return apps
    except Exception as e:
        return None

def download_app(app_name):
    """Download an app from GitHub"""
    try:
        # Ensure third_party_programs folder exists
        if not os.path.exists('third_party_programs'):
            os.makedirs('third_party_programs')
        
        url = GITHUB_RAW_URL + app_name
        target_path = f"third_party_programs/{app_name}"
        
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        return False

def app_store(stdscr):
    """App Store main function"""
    curses.curs_set(0)
    curses.start_color()
    init_colors()
    
    stdscr.bkgd(" ", curses.color_pair(5))
    
    menu_items = ["Browse Apps", "Refresh List", "Help", "Exit"]
    selected = 0
    
    while True:
        stdscr.clear()
        
        lines = [
            "=== Python-DOS App Store ===",
            "",
            "Download apps from the community",
            ""
        ]
        
        for item in menu_items:
            lines.append(item)
        
        lines.extend([
            "",
            "Repository:",
            "github.com/windowsuser688/Python-DOS-Apps",
            "",
            "UP/DOWN: Navigate | ENTER: Select | ESC: Exit"
        ])
        
        height, width = stdscr.getmaxyx()
        win_height = len(lines) + 4
        win_width = 70
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        draw_window(stdscr, win_y, win_x, win_width, win_height, "App Store", lines, selected + 4)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            break
        elif key == curses.KEY_UP:
            selected = (selected - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(menu_items)
        elif key in [10, 13]:  # ENTER
            choice = menu_items[selected]
            
            if choice == "Exit":
                break
            
            elif choice == "Browse Apps":
                browse_apps(stdscr)
            
            elif choice == "Refresh List":
                show_message(stdscr, "List will refresh on next browse")
            
            elif choice == "Help":
                show_help(stdscr)

def browse_apps(stdscr):
    """Browse and download apps"""
    stdscr.clear()
    stdscr.bkgd(" ", curses.color_pair(5))
    
    # Show loading message
    height, width = stdscr.getmaxyx()
    loading_lines = ["", "Fetching apps from GitHub...", "", "Please wait..."]
    draw_window(stdscr, height // 2 - 4, width // 2 - 20, 40, 8, "Loading", loading_lines)
    stdscr.refresh()
    
    # Fetch apps
    apps = fetch_available_apps()
    
    if apps is None:
        show_message(stdscr, "Error: Could not connect to GitHub\nCheck your internet connection")
        return
    
    if not apps:
        show_message(stdscr, "No apps found in repository\n\nThe repository may be empty or\ncontains no .py files")
        return
    
    # Show app list
    app_names = [app['name'] for app in apps]
    selected = 0
    scroll_offset = 0
    
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        lines = [
            f"=== Available Apps ({len(apps)}) ===",
            ""
        ]
        
        # Store the starting index for app names
        app_start_index = len(lines)
        
        for name in app_names:
            # Check if already installed
            if os.path.exists(f"third_party_programs/{name}"):
                lines.append(f"{name} [INSTALLED]")
            else:
                lines.append(name)
        
        lines.extend([
            "",
            "ENTER: Download | ESC: Back"
        ])
        
        # Calculate window size
        win_height = min(20, height - 4)  # Max 20 lines visible
        win_width = 70
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        # Adjust scroll offset to keep selection visible
        visible_lines = win_height - 2
        if selected < scroll_offset:
            scroll_offset = selected
        elif selected >= scroll_offset + visible_lines:
            scroll_offset = selected - visible_lines + 1
        
        # Adjust selected index for display (relative to app_start_index)
        display_selected = selected + app_start_index
        
        draw_window(stdscr, win_y, win_x, win_width, win_height, "Browse Apps", 
                   lines, display_selected, scroll_offset)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            break
        elif key == curses.KEY_UP:
            selected = (selected - 1) % len(app_names)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(app_names)
        elif key in [10, 13]:  # ENTER
            app_name = app_names[selected]
            
            # Validate that app ends with .py
            if not app_name.endswith('.py'):
                show_message(stdscr, f"Error: {app_name}\nMust be a .py file!")
                continue
            
            # Check if already installed
            if os.path.exists(f"third_party_programs/{app_name}"):
                show_message(stdscr, f"{app_name} is already installed!")
            else:
                # Download app
                stdscr.clear()
                stdscr.bkgd(" ", curses.color_pair(5))
                downloading_lines = ["", f"Downloading {app_name}...", "", "Please wait..."]
                draw_window(stdscr, height // 2 - 4, width // 2 - 25, 50, 8, "Downloading", downloading_lines)
                stdscr.refresh()
                
                if download_app(app_name):
                    show_message(stdscr, f"Success!\n{app_name} installed\n\nFind it in Third Party Programs")
                else:
                    show_message(stdscr, f"Error downloading {app_name}")

def show_help(stdscr):
    """Show help information"""
    stdscr.clear()
    stdscr.bkgd(" ", curses.color_pair(5))
    
    lines = [
        "=== App Store Help ===",
        "",
        "The App Store downloads apps from:",
        "github.com/windowsuser688/Python-DOS-Apps",
        "",
        "How to use:",
        "1. Select 'Browse Apps'",
        "2. Choose an app from the list",
        "3. Press ENTER to download",
        "4. App installs to third_party_programs/",
        "5. Run from 'Third Party Programs' menu",
        "",
        "Notes:",
        "- Requires internet connection",
        "- Apps marked [INSTALLED] are already on your system",
        "- Downloaded apps can be edited in App Maker",
        "",
        "Press any key to return..."
    ]
    
    height, width = stdscr.getmaxyx()
    win_height = len(lines) + 4
    win_width = 70
    win_y = (height - win_height) // 2
    win_x = (width - win_width) // 2
    
    draw_window(stdscr, win_y, win_x, win_width, win_height, "Help", lines)
    stdscr.refresh()
    stdscr.getch()

def main(stdscr):
    app_store(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
