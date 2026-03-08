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

def draw_window(stdscr, y, x, w, h, title, lines, cursor_pos=None):
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
            stdscr.addstr(y+1+i, x+2, line[:w-4], curses.color_pair(1))
    
    # Draw shadow
    stdscr.attron(curses.color_pair(4))
    for i in range(h):
        stdscr.addstr(y+i, x+w, " ")
    stdscr.addstr(y+h, x+1, " " * w)
    stdscr.attroff(curses.color_pair(4))

def notepad(stdscr):
    curses.curs_set(1)
    curses.start_color()
    init_colors()
    
    stdscr.bkgd(" ", curses.color_pair(5))
    
    text_lines = [""]
    cursor_line = 0
    cursor_col = 0
    scroll_offset = 0
    filename = "untitled.txt"
    modified = False
    
    while True:
        stdscr.clear()
        
        # Prepare display
        max_visible = 18
        visible_lines = text_lines[scroll_offset:scroll_offset + max_visible]
        
        # Pad lines to show cursor position
        display_lines = []
        for i, line in enumerate(visible_lines):
            display_lines.append(line[:70])
        
        # Add status bar
        status = f"File: {filename} {'*' if modified else ''} | Line {cursor_line+1}/{len(text_lines)}"
        controls = "F2: Save | F3: Save As | F4: Open | F5: New | F6: Rename | ESC: Menu"
        footer = ["=" * 70, status, controls]
        
        all_lines = display_lines + footer
        
        draw_window(stdscr, 2, 3, 75, len(all_lines)+2, "Notepad", all_lines)
        
        # Position cursor
        if cursor_line >= scroll_offset and cursor_line < scroll_offset + max_visible:
            display_cursor_line = cursor_line - scroll_offset
            stdscr.move(3 + display_cursor_line, 5 + min(cursor_col, 70))
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC - Show menu
            curses.curs_set(0)
            menu_choice = show_menu(stdscr, filename, modified, text_lines)
            curses.curs_set(1)
            
            if menu_choice == "exit":
                break
            elif menu_choice == "new":
                text_lines = [""]
                cursor_line = 0
                cursor_col = 0
                scroll_offset = 0
                filename = "untitled.txt"
                modified = False
            elif menu_choice.startswith("save:"):
                filename = menu_choice.split(":", 1)[1]
                try:
                    with open(filename, 'w') as f:
                        f.write('\n'.join(text_lines))
                    modified = False
                except:
                    pass
            elif menu_choice.startswith("open:"):
                filename = menu_choice.split(":", 1)[1]
                try:
                    with open(filename, 'r') as f:
                        text_lines = f.read().split('\n')
                        if not text_lines:
                            text_lines = [""]
                    cursor_line = 0
                    cursor_col = 0
                    scroll_offset = 0
                    modified = False
                except:
                    pass
            elif menu_choice.startswith("rename:"):
                new_filename = menu_choice.split(":", 1)[1]
                try:
                    # Save to new filename
                    with open(new_filename, 'w') as f:
                        f.write('\n'.join(text_lines))
                    # Delete old file if it exists and is different
                    if filename != "untitled.txt" and filename != new_filename:
                        try:
                            import os
                            os.remove(filename)
                        except:
                            pass
                    filename = new_filename
                    modified = False
                except:
                    pass
        
        elif key == curses.KEY_F2:  # F2 - Quick Save
            try:
                with open(filename, 'w') as f:
                    f.write('\n'.join(text_lines))
                modified = False
            except:
                pass
        
        elif key == curses.KEY_F3:  # F3 - Save As
            curses.curs_set(0)
            new_name = get_filename_input(stdscr, "Save As: ")
            curses.curs_set(1)
            if new_name:
                filename = new_name
                try:
                    with open(filename, 'w') as f:
                        f.write('\n'.join(text_lines))
                    modified = False
                except:
                    pass
        
        elif key == curses.KEY_F4:  # F4 - Open
            curses.curs_set(0)
            new_name = get_filename_input(stdscr, "Open File: ")
            curses.curs_set(1)
            if new_name:
                try:
                    with open(new_name, 'r') as f:
                        text_lines = f.read().split('\n')
                        if not text_lines:
                            text_lines = [""]
                    filename = new_name
                    cursor_line = 0
                    cursor_col = 0
                    scroll_offset = 0
                    modified = False
                except Exception as e:
                    # Show error if file doesn't exist
                    pass
        
        elif key == curses.KEY_F6:  # F6 - Rename
            curses.curs_set(0)
            new_name = get_filename_input(stdscr, "Rename to: ")
            curses.curs_set(1)
            if new_name:
                try:
                    # Save to new filename
                    with open(new_name, 'w') as f:
                        f.write('\n'.join(text_lines))
                    # Delete old file if it exists and is different
                    if filename != "untitled.txt" and filename != new_name:
                        try:
                            import os
                            os.remove(filename)
                        except:
                            pass
                    filename = new_name
                    modified = False
                except:
                    pass
        
        elif key == curses.KEY_F5:  # F5 - New
            if modified:
                curses.curs_set(0)
                confirm = confirm_dialog(stdscr, "Create new file without saving?")
                curses.curs_set(1)
                if confirm:
                    text_lines = [""]
                    cursor_line = 0
                    cursor_col = 0
                    scroll_offset = 0
                    filename = "untitled.txt"
                    modified = False
            else:
                text_lines = [""]
                cursor_line = 0
                cursor_col = 0
                scroll_offset = 0
                filename = "untitled.txt"
                modified = False
        
        elif key == curses.KEY_UP:
            if cursor_line > 0:
                cursor_line -= 1
                cursor_col = min(cursor_col, len(text_lines[cursor_line]))
                if cursor_line < scroll_offset:
                    scroll_offset = cursor_line
        
        elif key == curses.KEY_DOWN:
            if cursor_line < len(text_lines) - 1:
                cursor_line += 1
                cursor_col = min(cursor_col, len(text_lines[cursor_line]))
                if cursor_line >= scroll_offset + max_visible:
                    scroll_offset = cursor_line - max_visible + 1
        
        elif key == curses.KEY_LEFT:
            if cursor_col > 0:
                cursor_col -= 1
            elif cursor_line > 0:
                cursor_line -= 1
                cursor_col = len(text_lines[cursor_line])
        
        elif key == curses.KEY_RIGHT:
            if cursor_col < len(text_lines[cursor_line]):
                cursor_col += 1
            elif cursor_line < len(text_lines) - 1:
                cursor_line += 1
                cursor_col = 0
        
        elif key in [10, 13]:  # ENTER
            current_line = text_lines[cursor_line]
            text_lines[cursor_line] = current_line[:cursor_col]
            text_lines.insert(cursor_line + 1, current_line[cursor_col:])
            cursor_line += 1
            cursor_col = 0
            modified = True
            if cursor_line >= scroll_offset + max_visible:
                scroll_offset = cursor_line - max_visible + 1
        
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            if cursor_col > 0:
                text_lines[cursor_line] = text_lines[cursor_line][:cursor_col-1] + text_lines[cursor_line][cursor_col:]
                cursor_col -= 1
                modified = True
            elif cursor_line > 0:
                cursor_col = len(text_lines[cursor_line - 1])
                text_lines[cursor_line - 1] += text_lines[cursor_line]
                text_lines.pop(cursor_line)
                cursor_line -= 1
                modified = True
        
        elif 32 <= key <= 126:  # Printable characters
            text_lines[cursor_line] = text_lines[cursor_line][:cursor_col] + chr(key) + text_lines[cursor_line][cursor_col:]
            cursor_col += 1
            modified = True

def show_menu(stdscr, filename, modified, text_lines):
    menu_items = ["Continue Editing", "New File", "Save", "Save As", "Open File", "Rename File", "Exit"]
    selected = 0
    
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        lines = []
        for i, item in enumerate(menu_items):
            lines.append(item)
        
        # Draw menu window
        for i in range(len(lines)+4):
            stdscr.addstr(8+i, 25, " " * 35, curses.color_pair(1))
        
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(8, 25, "┌" + "─"*33 + "┐")
        for i in range(1, len(lines)+3):
            stdscr.addstr(8+i, 25, "│" + " "*33 + "│")
        stdscr.addstr(8+len(lines)+3, 25, "└" + "─"*33 + "┘")
        stdscr.attroff(curses.color_pair(2))
        
        stdscr.addstr(8, 27, " File Menu ", curses.color_pair(1))
        
        for i, item in enumerate(menu_items):
            if i == selected:
                stdscr.addstr(9+i, 27, item, curses.color_pair(3))
            else:
                stdscr.addstr(9+i, 27, item, curses.color_pair(1))
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(menu_items)
        elif key in [10, 13]:
            choice = menu_items[selected]
            
            if choice == "Continue Editing":
                return "continue"
            elif choice == "New File":
                return "new"
            elif choice == "Save":
                return f"save:{filename}"
            elif choice == "Save As":
                new_name = get_filename_input(stdscr, "Save As: ")
                if new_name:
                    return f"save:{new_name}"
            elif choice == "Open File":
                new_name = get_filename_input(stdscr, "Open File: ")
                if new_name:
                    return f"open:{new_name}"
            elif choice == "Rename File":
                new_name = get_filename_input(stdscr, "Rename to: ")
                if new_name:
                    return f"rename:{new_name}"
            elif choice == "Exit":
                if modified:
                    confirm = confirm_dialog(stdscr, "Exit without saving?")
                    if confirm:
                        return "exit"
                else:
                    return "exit"
        elif key == 27:
            return "continue"

def get_filename_input(stdscr, prompt):
    curses.curs_set(1)
    filename = ""
    current_folder = "Documents"  # Default to Documents
    
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        # Draw input box
        for i in range(11):
            stdscr.addstr(9+i, 15, " " * 55, curses.color_pair(1))
        
        stdscr.addstr(10, 17, prompt, curses.color_pair(1))
        stdscr.addstr(11, 17, f"Folder: {current_folder}", curses.color_pair(1))
        stdscr.addstr(12, 17, filename[:45], curses.color_pair(1))
        stdscr.addstr(14, 17, "TAB: Switch Folder (Documents/Downloads)", curses.color_pair(1))
        stdscr.addstr(15, 17, "ENTER: Confirm | ESC: Cancel", curses.color_pair(1))
        
        full_path = f"usr/root/{current_folder}/{filename}" if filename else ""
        if full_path:
            stdscr.addstr(17, 17, f"Path: {full_path[:40]}", curses.color_pair(1))
        
        stdscr.move(12, 17 + len(filename[:45]))
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            curses.curs_set(0)
            return None
        elif key in [10, 13]:  # ENTER
            curses.curs_set(0)
            if filename:
                return f"usr/root/{current_folder}/{filename}"
            return None
        elif key == 9:  # TAB - Switch folder
            current_folder = "Downloads" if current_folder == "Documents" else "Documents"
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            if filename:
                filename = filename[:-1]
        elif 32 <= key <= 126:
            filename += chr(key)

def confirm_dialog(stdscr, message):
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        for i in range(6):
            stdscr.addstr(10+i, 20, " " * 45, curses.color_pair(1))
        
        stdscr.addstr(11, 22, message, curses.color_pair(1))
        stdscr.addstr(13, 22, "Y: Yes | N: No", curses.color_pair(1))
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key in [ord('y'), ord('Y')]:
            return True
        elif key in [ord('n'), ord('N'), 27]:
            return False

def main(stdscr):
    notepad(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
