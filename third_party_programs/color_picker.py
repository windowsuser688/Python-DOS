"""
Color Picker App for Python-DOS
Browse through different color combinations
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

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'apps'))

try:
    from config_loader import init_colors
except ImportError:
    def init_colors():
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
        except:
            config = {"background_color": "blue", "selection_color": "red"}
        
        color_map = {
            "black": curses.COLOR_BLACK, "red": curses.COLOR_RED,
            "green": curses.COLOR_GREEN, "yellow": curses.COLOR_YELLOW,
            "blue": curses.COLOR_BLUE, "magenta": curses.COLOR_MAGENTA,
            "cyan": curses.COLOR_CYAN, "white": curses.COLOR_WHITE
        }
        
        bg_color = color_map.get(config.get('background_color', 'blue'), curses.COLOR_BLUE)
        sel_color = color_map.get(config.get('selection_color', 'red'), curses.COLOR_RED)
        
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_WHITE, sel_color)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_WHITE, bg_color)

def draw_window(stdscr, y, x, w, h, title, lines):
    for i in range(h):
        stdscr.addstr(y+i, x, " " * w, curses.color_pair(1))
    
    stdscr.attron(curses.color_pair(2))
    stdscr.addstr(y, x, "┌" + "─"*(w-2) + "┐")
    for i in range(1, h-1):
        stdscr.addstr(y+i, x, "│" + " "*(w-2) + "│")
    stdscr.addstr(y+h-1, x, "└" + "─"*(w-2) + "┘")
    stdscr.attroff(curses.color_pair(2))
    
    stdscr.addstr(y, x+2, f" {title} ", curses.color_pair(1))
    
    for i, line in enumerate(lines):
        if i < h-2:
            stdscr.addstr(y+1+i, x+2, line[:w-4], curses.color_pair(1))
    
    stdscr.attron(curses.color_pair(4))
    for i in range(h):
        stdscr.addstr(y+i, x+w, " ")
    stdscr.addstr(y+h, x+1, " " * w)
    stdscr.attroff(curses.color_pair(4))

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    
    colors = [
        ("Black", curses.COLOR_BLACK),
        ("Red", curses.COLOR_RED),
        ("Green", curses.COLOR_GREEN),
        ("Yellow", curses.COLOR_YELLOW),
        ("Blue", curses.COLOR_BLUE),
        ("Magenta", curses.COLOR_MAGENTA),
        ("Cyan", curses.COLOR_CYAN),
        ("White", curses.COLOR_WHITE)
    ]
    
    selected = 0
    
    # Initialize color pairs
    for i, (name, color) in enumerate(colors):
        curses.init_pair(i + 10, curses.COLOR_WHITE, color)
    
    init_colors()
    stdscr.bkgd(" ", curses.color_pair(5))
    
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        lines = [
            "=== Color Preview ===",
            ""
        ]
        
        for i, (name, color) in enumerate(colors):
            if i == selected:
                lines.append(f"> {name}")
            else:
                lines.append(f"  {name}")
        
        lines.extend([
            "",
            "UP/DOWN: Navigate",
            "ESC: Exit"
        ])
        
        win_height = len(lines) + 4
        win_width = 40
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        draw_window(stdscr, win_y, win_x, win_width, win_height, "Color Picker", lines)
        
        # Draw color preview box
        preview_y = win_y + 2
        preview_x = win_x + win_width + 5
        preview_w = 20
        preview_h = 5
        
        try:
            for i in range(preview_h):
                stdscr.addstr(preview_y + i, preview_x, " " * preview_w, curses.color_pair(selected + 10))
            stdscr.addstr(preview_y + preview_h, preview_x + 2, colors[selected][0], curses.color_pair(1))
        except:
            pass
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            break
        elif key == curses.KEY_UP:
            selected = (selected - 1) % len(colors)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(colors)

if __name__ == "__main__":
    curses.wrapper(main)
