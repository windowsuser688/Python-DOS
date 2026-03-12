try:
    import curses
except ImportError:
    print("ERROR: curses library not found!")
    print("Please install it with: pip install windows-curses")
    input("Press Enter to exit...")
    exit(1)

import sys
import os
import subprocess
import tempfile
import threading
import time

# Set terminal type for simulated terminals
os.environ['TERM'] = 'xterm-256color'

sys.path.insert(0, os.path.dirname(__file__))
from config_loader import init_colors

def draw_window(stdscr, y, x, w, h, title, lines, selected=None):
    """Draw a window with border and shadow"""
    max_y, max_x = stdscr.getmaxyx()
    
    # Ensure window fits on screen
    if y + h >= max_y:
        h = max_y - y - 1
    if x + w >= max_x:
        w = max_x - x - 1
    
    if h < 3 or w < 3:
        return  # Window too small
    
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
    start_line = max(0, (selected or 0) - (h - 4)) if selected is not None else 0
    
    for i, line_idx in enumerate(range(start_line, min(start_line + h - 2, len(lines)))):
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
    
    lines = [message, "", "Press any key to continue"]
    
    height, width = stdscr.getmaxyx()
    win_height = 8
    win_width = 50
    win_y = (height - win_height) // 2
    win_x = (width - win_width) // 2
    
    draw_window(stdscr, win_y, win_x, win_width, win_height, "Message", lines)
    stdscr.refresh()
    stdscr.getch()

def get_text_input(stdscr, prompt, max_length=30):
    """Get text input from user"""
    curses.curs_set(1)
    text = ""
    
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        height, width = stdscr.getmaxyx()
        
        lines = [
            "",
            prompt,
            "",
            text + "_",
            "",
            "ENTER: Confirm | ESC: Cancel",
            "BACKSPACE: Delete"
        ]
        
        win_height = len(lines) + 4
        win_width = 60
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        draw_window(stdscr, win_y, win_x, win_width, win_height, "Input", lines)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            curses.curs_set(0)
            return None
        elif key in [10, 13]:  # ENTER
            curses.curs_set(0)
            return text if text else None
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            if text:
                text = text[:-1]
        elif 32 <= key <= 126 and len(text) < max_length:
            char = chr(key)
            if char.isalnum() or char == '_':
                text += char

def app_maker_ide(stdscr, app_path):
    """Three-panel IDE: Editor, Preview, Terminal"""
    curses.curs_set(0)
    
    # Load app code
    try:
        with open(app_path, 'r', encoding='utf-8') as f:
            code_lines = f.read().split('\n')
    except:
        code_lines = ["# Error loading file"]
    
    current_line = 0
    scroll_offset = 0
    terminal_output = ["Terminal ready. Press F5 to run app."]
    preview_active = False
    
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        height, width = stdscr.getmaxyx()
        
        # Calculate panel sizes
        editor_width = width // 2 - 2
        preview_width = width // 2 - 2
        editor_height = height - 12
        terminal_height = 8
        
        # Draw Editor panel (left)
        editor_lines = []
        for i, line in enumerate(code_lines[scroll_offset:scroll_offset + editor_height - 2]):
            line_num = scroll_offset + i + 1
            editor_lines.append(f"{line_num:3} | {line[:editor_width-8]}")
        
        draw_window(stdscr, 2, 2, editor_width, editor_height, 
                   f"Editor: {os.path.basename(app_path)}", editor_lines, current_line - scroll_offset)
        
        # Draw Preview panel (right)
        if preview_active:
            preview_lines = ["App is running...", "", "Close app window to return"]
        else:
            preview_lines = ["Preview Window", "", "Press F5 to run your app", "", 
                           "The app will open in a new window"]
        
        draw_window(stdscr, 2, editor_width + 4, preview_width, editor_height, 
                   "Preview", preview_lines)
        
        # Draw Terminal panel (bottom, full width)
        terminal_display = terminal_output[-terminal_height+2:]
        draw_window(stdscr, editor_height + 2, 2, width - 4, terminal_height, 
                   "Terminal / Errors", terminal_display)
        
        # Draw controls
        controls = "F2:Save | F5:Run | F6:Edit in Notepad | ESC:Exit"
        try:
            if height - 1 < height and len(controls) < width - 4:
                stdscr.addstr(height - 1, 2, controls[:width-4], curses.color_pair(1))
        except:
            pass
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            break
        
        elif key == curses.KEY_UP:
            if current_line > 0:
                current_line -= 1
                if current_line < scroll_offset:
                    scroll_offset = current_line
        
        elif key == curses.KEY_DOWN:
            if current_line < len(code_lines) - 1:
                current_line += 1
                if current_line >= scroll_offset + editor_height - 2:
                    scroll_offset = current_line - editor_height + 3
        
        elif key == curses.KEY_F2:  # Save
            try:
                with open(app_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(code_lines))
                terminal_output.append(f"[SAVED] File saved successfully")
            except Exception as e:
                terminal_output.append(f"[ERROR] Save failed: {str(e)}")
        
        elif key == curses.KEY_F5:  # Run app
            terminal_output.append(f"[RUN] Launching {os.path.basename(app_path)}...")
            stdscr.refresh()
            
            # Run the app in a visible window (don't capture output)
            curses.endwin()
            
            # Run without capturing so the GUI shows
            result = subprocess.run(["python", app_path])
            
            # Reinitialize curses properly
            stdscr.clear()
            stdscr.refresh()
            curses.start_color()
            init_colors()
            stdscr.bkgd(" ", curses.color_pair(5))
            curses.curs_set(0)
            stdscr.keypad(True)
            
            if result.returncode == 0:
                terminal_output.append(f"[SUCCESS] App exited normally (code 0)")
            else:
                terminal_output.append(f"[ERROR] App exited with code {result.returncode}")
                terminal_output.append(f"  Check for syntax errors or crashes")
        
        elif key == curses.KEY_F6:  # Edit in Notepad
            terminal_output.append(f"[EDIT] Opening in Notepad...")
            curses.endwin()
            subprocess.run(["python", "apps/notepad.py"])
            
            # Reload file after editing
            try:
                with open(app_path, 'r', encoding='utf-8') as f:
                    code_lines = f.read().split('\n')
                terminal_output.append(f"[RELOAD] File reloaded from disk")
            except:
                terminal_output.append(f"[ERROR] Failed to reload file")
            
            # Reinitialize curses properly
            stdscr.clear()
            stdscr.refresh()
            curses.start_color()
            init_colors()
            stdscr.bkgd(" ", curses.color_pair(5))
            curses.curs_set(0)
            stdscr.keypad(True)

def app_maker(stdscr):
    """App Maker main function"""
    curses.curs_set(0)
    curses.start_color()
    init_colors()
    
    stdscr.bkgd(" ", curses.color_pair(5))
    
    menu_items = ["Create New App", "Open Existing App", "Help", "Exit"]
    selected = 0
    
    while True:
        stdscr.clear()
        
        lines = [
            "=== App Maker IDE ===",
            "",
            "Create and edit Python-DOS apps",
            ""
        ]
        
        for item in menu_items:
            lines.append(item)
        
        lines.extend([
            "",
            "Features:",
            "- Code editor with line numbers",
            "- Live preview by running app",
            "- Terminal for errors and output",
            "",
            "UP/DOWN: Navigate | ENTER: Select | ESC: Exit"
        ])
        
        height, width = stdscr.getmaxyx()
        win_height = len(lines) + 4
        win_width = 70
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        draw_window(stdscr, win_y, win_x, win_width, win_height, "App Maker", lines, selected + 4)
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
            
            elif choice == "Create New App":
                app_name = get_text_input(stdscr, "Enter app name (no spaces):")
                
                if app_name:
                    target_path = f"third_party_programs/{app_name}.py"
                    
                    if os.path.exists(target_path):
                        show_message(stdscr, f"Error: {app_name}.py already exists!")
                    else:
                        template_path = "third_party_programs/app_template.py"
                        
                        try:
                            with open(template_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            content = content.replace("Your App Name", app_name.replace('_', ' ').title())
                            content = content.replace("your_app_name", app_name)
                            
                            with open(target_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            # Open in IDE
                            app_maker_ide(stdscr, target_path)
                            
                            # Reinitialize after IDE
                            curses.start_color()
                            init_colors()
                            stdscr.bkgd(" ", curses.color_pair(5))
                            curses.curs_set(0)
                        
                        except Exception as e:
                            show_message(stdscr, f"Error: {str(e)}")
            
            elif choice == "Open Existing App":
                # List existing apps
                import glob
                apps = glob.glob("third_party_programs/*.py")
                apps = [a for a in apps if not a.endswith("app_template.py")]
                
                if not apps:
                    show_message(stdscr, "No apps found. Create one first!")
                else:
                    app_selected = select_from_list(stdscr, "Select App to Edit", 
                                                    [os.path.basename(a) for a in apps])
                    if app_selected is not None:
                        app_maker_ide(stdscr, apps[app_selected])
                        
                        # Reinitialize after IDE
                        curses.start_color()
                        init_colors()
                        stdscr.bkgd(" ", curses.color_pair(5))
                        curses.curs_set(0)
            
            elif choice == "Help":
                show_help(stdscr)

def select_from_list(stdscr, title, items):
    """Select an item from a list"""
    selected = 0
    
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        lines = []
        for item in items:
            lines.append(item)
        lines.append("")
        lines.append("UP/DOWN: Navigate | ENTER: Select | ESC: Cancel")
        
        height, width = stdscr.getmaxyx()
        win_height = min(len(lines) + 4, height - 4)
        win_width = 60
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        draw_window(stdscr, win_y, win_x, win_width, win_height, title, lines, selected)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            return None
        elif key == curses.KEY_UP:
            selected = (selected - 1) % len(items)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(items)
        elif key in [10, 13]:  # ENTER
            return selected

def show_help(stdscr):
    """Show help information"""
    stdscr.clear()
    stdscr.bkgd(" ", curses.color_pair(5))
    
    lines = [
        "=== App Maker IDE Help ===",
        "",
        "Creating Apps:",
        "1. Select 'Create New App'",
        "2. Enter a name (alphanumeric, underscores)",
        "3. IDE opens with template code",
        "",
        "IDE Controls:",
        "F2 - Save current file",
        "F5 - Run/Preview app",
        "F6 - Edit in full Notepad",
        "UP/DOWN - Navigate code",
        "ESC - Exit IDE",
        "",
        "The IDE has 3 panels:",
        "- Editor: View/navigate code",
        "- Preview: Run your app",
        "- Terminal: See errors and output",
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
    app_maker(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)

