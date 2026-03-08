try:
    import curses
except ImportError:
    print("ERROR: curses library not found!")
    print("Please install it with: pip install windows-curses")
    input("Press Enter to exit...")
    exit(1)

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from config_loader import load_config, init_colors

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
                stdscr.addstr(y+1+i, x+2, line[:w-4], curses.color_pair(3))
            else:
                stdscr.addstr(y+1+i, x+2, line[:w-4], curses.color_pair(1))
    
    # Draw shadow
    stdscr.attron(curses.color_pair(4))
    for i in range(h):
        stdscr.addstr(y+i, x+w, " ")
    stdscr.addstr(y+h, x+1, " " * w)
    stdscr.attroff(curses.color_pair(4))

def file_explorer(stdscr):
    curses.curs_set(0)
    curses.start_color()
    init_colors()
    
    config = load_config()
    stdscr.bkgd(" ", curses.color_pair(5))
    
    current_path = os.getcwd()
    selected = 0
    scroll_offset = 0
    
    while True:
        stdscr.clear()
        
        try:
            items = [".."] + sorted(os.listdir(current_path))
        except PermissionError:
            items = [".. (Permission Denied)"]
        
        # Prepare display lines
        display_lines = []
        for item in items:
            full_path = os.path.join(current_path, item)
            if item == "..":
                display_lines.append("[DIR] ..")
            elif os.path.isdir(full_path):
                display_lines.append(f"[DIR] {item}")
            else:
                display_lines.append(f"[FILE] {item}")
        
        # Calculate visible window
        max_visible = 15
        visible_items = display_lines[scroll_offset:scroll_offset + max_visible]
        
        # Add header
        header = [f"Path: {current_path[:50]}", "=" * 50, ""]
        footer = ["", "UP/DOWN: Navigate | ENTER: Open | ESC: Exit"]
        
        all_lines = header + visible_items + footer
        
        draw_window(stdscr, 3, 5, 70, len(all_lines)+2, "File Explorer", all_lines, 
                   selected - scroll_offset + 3 if selected - scroll_offset < max_visible else None)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            break
        
        elif key == curses.KEY_UP:
            if selected > 0:
                selected -= 1
                if selected < scroll_offset:
                    scroll_offset = selected
        
        elif key == curses.KEY_DOWN:
            if selected < len(items) - 1:
                selected += 1
                if selected >= scroll_offset + max_visible:
                    scroll_offset = selected - max_visible + 1
        
        elif key in [10, 13]:  # ENTER
            selected_item = items[selected]
            
            if selected_item == "..":
                current_path = os.path.dirname(current_path)
                selected = 0
                scroll_offset = 0
            else:
                full_path = os.path.join(current_path, selected_item)
                if os.path.isdir(full_path):
                    current_path = full_path
                    selected = 0
                    scroll_offset = 0

def main(stdscr):
    file_explorer(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
