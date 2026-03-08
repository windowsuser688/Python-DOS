try:
    import curses
except ImportError:
    print("ERROR: curses library not found!")
    print("Please install it with: pip install windows-curses")
    input("Press Enter to exit...")
    exit(1)

import os
import sys
import subprocess
import tempfile
sys.path.insert(0, os.path.dirname(__file__))
from config_loader import load_config, init_colors

def draw_window(stdscr, y, x, w, h, title, lines, cursor_pos=None):
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
            stdscr.addstr(y+1+i, x+2, line[:w-4], curses.color_pair(1))
    
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

def get_filename_input(stdscr, prompt, is_save=True):
    """Get filename input with folder selection"""
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
        
        # Get current user from config
        try:
            import json
            with open('config.json', 'r') as f:
                config = json.load(f)
            current_user = config.get('current_user', 'root')
        except:
            current_user = 'root'
        
        full_path = f"usr/{current_user}/{current_folder}/{filename}" if filename else ""
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
                # Ensure .py extension
                if not filename.endswith('.py'):
                    filename += '.py'
                return f"usr/{current_user}/{current_folder}/{filename}"
            return None
        elif key == 9:  # TAB - Switch folder
            current_folder = "Downloads" if current_folder == "Documents" else "Documents"
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            if filename:
                filename = filename[:-1]
        elif 32 <= key <= 126:
            filename += chr(key)

def python_ide(stdscr):
    curses.curs_set(1)
    curses.start_color()
    init_colors()
    
    stdscr.bkgd(" ", curses.color_pair(5))
    
    # Editor state
    code_lines = ["# Python IDE", "# Write your Python code here", ""]
    cursor_line = 2
    cursor_col = 0
    scroll_offset = 0
    
    # Terminal output
    terminal_output = ["Python-DOS IDE Terminal", "Press F5 to run code", ""]
    
    filename = "untitled.py"
    
    while True:
        stdscr.clear()
        
        height, width = stdscr.getmaxyx()
        
        # Calculate split
        editor_height = (height - 6) // 2
        terminal_height = height - editor_height - 6
        
        # Prepare editor display
        max_visible = editor_height - 2
        visible_code = code_lines[scroll_offset:scroll_offset + max_visible]
        
        editor_lines = []
        for i, line in enumerate(visible_code):
            line_num = scroll_offset + i + 1
            editor_lines.append(f"{line_num:3} | {line[:60]}")
        
        # Draw editor window
        draw_window(stdscr, 2, 3, 70, editor_height, f"Editor - {filename}", editor_lines)
        
        # Position cursor in editor
        if cursor_line >= scroll_offset and cursor_line < scroll_offset + max_visible:
            display_cursor_line = cursor_line - scroll_offset
            stdscr.move(3 + display_cursor_line, 11 + min(cursor_col, 60))
        
        # Prepare terminal display
        terminal_lines = terminal_output[-terminal_height+2:]
        
        # Draw terminal window
        draw_window(stdscr, 2 + editor_height, 3, 70, terminal_height, "Terminal Output", terminal_lines)
        
        # Draw status bar
        status = f"F5: Run | F2: Save | F3: Load | F4: Clear | ESC: Exit | Line {cursor_line+1}/{len(code_lines)}"
        stdscr.addstr(height - 2, 3, status[:width-6], curses.color_pair(1))
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            break
        
        elif key == curses.KEY_F5:  # F5 - Run code
            terminal_output.append("=" * 60)
            terminal_output.append("Running code...")
            terminal_output.append("")
            
            # Save code to temp file and run
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write('\n'.join(code_lines))
                    temp_file = f.name
                
                # Run the code
                result = subprocess.run(
                    ['python', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                # Show output
                if result.stdout:
                    for line in result.stdout.split('\n'):
                        terminal_output.append(line)
                
                if result.stderr:
                    terminal_output.append("--- Errors ---")
                    for line in result.stderr.split('\n'):
                        terminal_output.append(line)
                
                if result.returncode == 0:
                    terminal_output.append("")
                    terminal_output.append("Program finished successfully")
                else:
                    terminal_output.append("")
                    terminal_output.append(f"Program exited with code {result.returncode}")
                
                # Clean up temp file
                os.unlink(temp_file)
                
            except subprocess.TimeoutExpired:
                terminal_output.append("Error: Program timed out (5 second limit)")
            except Exception as e:
                terminal_output.append(f"Error: {e}")
            
            terminal_output.append("")
        
        elif key == curses.KEY_F2:  # F2 - Save
            save_path = get_filename_input(stdscr, "Save as:", is_save=True)
            if save_path:
                try:
                    # Ensure directory exists
                    import os
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    
                    with open(save_path, 'w') as f:
                        f.write('\n'.join(code_lines))
                    filename = os.path.basename(save_path)
                    terminal_output.append(f"Saved to {save_path}")
                except Exception as e:
                    terminal_output.append(f"Error saving: {e}")
        
        elif key == curses.KEY_F3:  # F3 - Load
            load_path = get_filename_input(stdscr, "Load file:", is_save=False)
            if load_path:
                try:
                    with open(load_path, 'r') as f:
                        code_lines = f.read().split('\n')
                        if not code_lines:
                            code_lines = [""]
                    cursor_line = 0
                    cursor_col = 0
                    scroll_offset = 0
                    filename = os.path.basename(load_path)
                    terminal_output.append(f"Loaded {load_path}")
                except Exception as e:
                    terminal_output.append(f"Error loading: {e}")
        
        elif key == curses.KEY_F4:  # F4 - Clear terminal
            terminal_output = ["Terminal cleared"]
        
        elif key == curses.KEY_UP:
            if cursor_line > 0:
                cursor_line -= 1
                cursor_col = min(cursor_col, len(code_lines[cursor_line]))
                if cursor_line < scroll_offset:
                    scroll_offset = cursor_line
        
        elif key == curses.KEY_DOWN:
            if cursor_line < len(code_lines) - 1:
                cursor_line += 1
                cursor_col = min(cursor_col, len(code_lines[cursor_line]))
                if cursor_line >= scroll_offset + max_visible:
                    scroll_offset = cursor_line - max_visible + 1
        
        elif key == curses.KEY_LEFT:
            if cursor_col > 0:
                cursor_col -= 1
            elif cursor_line > 0:
                cursor_line -= 1
                cursor_col = len(code_lines[cursor_line])
        
        elif key == curses.KEY_RIGHT:
            if cursor_col < len(code_lines[cursor_line]):
                cursor_col += 1
            elif cursor_line < len(code_lines) - 1:
                cursor_line += 1
                cursor_col = 0
        
        elif key in [10, 13]:  # ENTER
            current_line = code_lines[cursor_line]
            code_lines[cursor_line] = current_line[:cursor_col]
            code_lines.insert(cursor_line + 1, current_line[cursor_col:])
            cursor_line += 1
            cursor_col = 0
            if cursor_line >= scroll_offset + max_visible:
                scroll_offset = cursor_line - max_visible + 1
        
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            if cursor_col > 0:
                code_lines[cursor_line] = code_lines[cursor_line][:cursor_col-1] + code_lines[cursor_line][cursor_col:]
                cursor_col -= 1
            elif cursor_line > 0:
                cursor_col = len(code_lines[cursor_line - 1])
                code_lines[cursor_line - 1] += code_lines[cursor_line]
                code_lines.pop(cursor_line)
                cursor_line -= 1
        
        elif key == 9:  # TAB
            code_lines[cursor_line] = code_lines[cursor_line][:cursor_col] + "    " + code_lines[cursor_line][cursor_col:]
            cursor_col += 4
        
        elif 32 <= key <= 126:  # Printable characters
            code_lines[cursor_line] = code_lines[cursor_line][:cursor_col] + chr(key) + code_lines[cursor_line][cursor_col:]
            cursor_col += 1

def main(stdscr):
    python_ide(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
