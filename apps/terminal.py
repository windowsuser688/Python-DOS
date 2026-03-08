try:
    import curses
except ImportError:
    print("ERROR: curses library not found!")
    print("Please install it with: pip install windows-curses")
    input("Press Enter to exit...")
    exit(1)

import subprocess
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from config_loader import load_config, init_colors

def draw_window(stdscr, y, x, w, h, title, lines):
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

def terminal(stdscr):
    curses.curs_set(1)
    curses.start_color()
    init_colors()
    
    stdscr.bkgd(" ", curses.color_pair(5))
    
    output_lines = ["Python-DOS Terminal v1.0", "Type 'help' for commands, 'exit' to quit", ""]
    command_input = ""
    
    while True:
        stdscr.clear()
        
        # Prepare display
        display_lines = output_lines[-15:] + [f"> {command_input}"]
        
        draw_window(stdscr, 3, 5, 70, 20, "Terminal", display_lines)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            break
        
        elif key in [10, 13]:  # ENTER
            if command_input.strip():
                output_lines.append(f"> {command_input}")
                
                if command_input.strip() == "exit":
                    break
                elif command_input.strip() == "help":
                    output_lines.append("Available commands:")
                    output_lines.append("  help - Show this help")
                    output_lines.append("  clear - Clear screen")
                    output_lines.append("  dir/ls - List files")
                    output_lines.append("  cd <path> - Change directory")
                    output_lines.append("  pwd - Show current directory")
                    output_lines.append("  exit - Exit terminal")
                elif command_input.strip() == "clear":
                    output_lines = []
                elif command_input.strip() in ["dir", "ls"]:
                    try:
                        files = os.listdir(".")
                        for f in files:
                            output_lines.append(f"  {f}")
                    except Exception as e:
                        output_lines.append(f"Error: {e}")
                elif command_input.strip() == "pwd":
                    output_lines.append(os.getcwd())
                elif command_input.strip().startswith("cd "):
                    path = command_input.strip()[3:]
                    try:
                        os.chdir(path)
                        output_lines.append(f"Changed to: {os.getcwd()}")
                    except Exception as e:
                        output_lines.append(f"Error: {e}")
                else:
                    # Try to execute as system command
                    try:
                        result = subprocess.run(command_input, shell=True, capture_output=True, 
                                              text=True, timeout=5)
                        if result.stdout:
                            for line in result.stdout.split('\n')[:10]:
                                output_lines.append(line)
                        if result.stderr:
                            output_lines.append(f"Error: {result.stderr[:100]}")
                    except subprocess.TimeoutExpired:
                        output_lines.append("Command timed out")
                    except Exception as e:
                        output_lines.append(f"Command not found: {command_input}")
                
                command_input = ""
        
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            if command_input:
                command_input = command_input[:-1]
        
        elif 32 <= key <= 126:  # Printable characters
            command_input += chr(key)

def main(stdscr):
    terminal(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
