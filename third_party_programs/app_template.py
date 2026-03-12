"""
Python-DOS App Template
Copy this file to apps/ folder and modify it to create your own app.

Instructions:
1. Copy this file to apps/your_app_name.py
2. Modify the app_main() function with your app logic
3. Update the window title and content
4. Add your app to the main menu in shell.py

Features included:
- Curses initialization with error handling
- Color scheme loading from config
- Window drawing with shadow
- Navigation with arrow keys
- ESC to exit
"""

try:
    import curses
except ImportError:
    print("ERROR: curses library not found!")
    print("Please install it with: pip install windows-curses")
    input("Press Enter to exit...")
    exit(1)

import sys
import os
import json

# Try to import config_loader from apps folder
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'apps'))

try:
    from config_loader import init_colors
except ImportError:
    # If config_loader not found, define init_colors locally
    def init_colors():
        """Initialize color pairs from config"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
        except:
            config = {
                "background_color": "blue",
                "selection_color": "red"
            }
        
        # Map color names to curses colors
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
        
        bg_color = color_map.get(config.get('background_color', 'blue'), curses.COLOR_BLUE)
        sel_color = color_map.get(config.get('selection_color', 'red'), curses.COLOR_RED)
        
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)   # window fill
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)   # borders
        curses.init_pair(3, curses.COLOR_WHITE, sel_color)            # selection
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)   # shadow
        curses.init_pair(5, curses.COLOR_WHITE, bg_color)             # desktop bg


def draw_window(stdscr, y, x, w, h, title, lines, selected=None):
    """Draw a window with border and shadow"""
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
                stdscr.addstr(y+1+i, x+2, line[:w-4], curses.color_pair(3))
            else:
                stdscr.addstr(y+1+i, x+2, line[:w-4], curses.color_pair(1))
    
    # Draw shadow
    stdscr.attron(curses.color_pair(4))
    for i in range(h):
        stdscr.addstr(y+i, x+w, " ")
    stdscr.addstr(y+h, x+1, " " * w)
    stdscr.attroff(curses.color_pair(4))

def app_main(stdscr):
    """Main app logic - modify this function"""
    curses.curs_set(0)
    curses.start_color()
    init_colors()
    
    stdscr.bkgd(" ", curses.color_pair(5))
    
    # Example: Simple menu
    menu_items = ["Option 1", "Option 2", "Option 3", "Exit"]
    selected = 0
    
    while True:
        stdscr.clear()
        
        # Prepare content with clear instructions
        lines = [
            "=== Your App Name ===",
            "",
            "Select an option:",
            ""
        ]
        
        # Add menu items
        for item in menu_items:
            lines.append(item)
        
        lines.extend([
            "",
            "=== Controls ===",
            "UP/DOWN: Navigate",
            "ENTER: Select",
            "ESC: Exit to Main Menu"
        ])
        
        # Draw window
        height, width = stdscr.getmaxyx()
        win_height = len(lines) + 4
        win_width = 50
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        draw_window(stdscr, win_y, win_x, win_width, win_height, "Your App Name", lines, selected + 4)
        stdscr.refresh()
        
        # Handle input
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
            elif choice == "Option 1":
                # Handle Option 1
                show_message(stdscr, "You selected Option 1!")
            elif choice == "Option 2":
                # Handle Option 2
                show_message(stdscr, "You selected Option 2!")
            elif choice == "Option 3":
                # Handle Option 3
                show_message(stdscr, "You selected Option 3!")

def show_message(stdscr, message):
    """Show a simple message dialog"""
    stdscr.clear()
    stdscr.bkgd(" ", curses.color_pair(5))
    
    lines = [message, "", "Press any key to continue"]
    
    height, width = stdscr.getmaxyx()
    win_height = 8
    win_width = 40
    win_y = (height - win_height) // 2
    win_x = (width - win_width) // 2
    
    draw_window(stdscr, win_y, win_x, win_width, win_height, "Message", lines)
    stdscr.refresh()
    stdscr.getch()

def main(stdscr):
    app_main(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
