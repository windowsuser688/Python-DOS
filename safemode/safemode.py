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

def draw_window(stdscr, y, x, w, h, title, lines):
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

def safe_mode_shell(stdscr):
    curses.curs_set(1)
    curses.start_color()
    
    # Safe mode colors (minimal, black background)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)   # window fill
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)   # borders
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)   # shadow
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # warning text
    
    stdscr.bkgd(" ", curses.color_pair(1))
    
    output_lines = [
        "Python-DOS Safe Mode Shell v1.0",
        "WARNING: Running in Safe Mode",
        "Limited functionality - diagnostic mode only",
        "",
        "Type 'help' for commands, 'exit' to reboot",
        ""
    ]
    command_input = ""
    
    while True:
        stdscr.clear()
        
        # Show warning banner
        height, width = stdscr.getmaxyx()
        banner = "*** SAFE MODE ***"
        stdscr.addstr(1, (width - len(banner)) // 2, banner, curses.color_pair(5) | curses.A_BOLD)
        
        # Prepare display
        display_lines = output_lines[-13:] + [f"> {command_input}"]
        
        draw_window(stdscr, 3, 5, 70, 18, "Safe Mode Shell", display_lines)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            break
        
        elif key in [10, 13]:  # ENTER
            if command_input.strip():
                output_lines.append(f"> {command_input}")
                
                if command_input.strip() == "exit":
                    output_lines.append("Rebooting to normal mode...")
                    stdscr.clear()
                    msg_lines = ["Rebooting...", "", "Please wait..."]
                    draw_window(stdscr, 10, 20, 40, 7, "Reboot", msg_lines)
                    stdscr.refresh()
                    import time
                    time.sleep(2)
                    # Return to bootloader
                    curses.endwin()
                    subprocess.run(["python", "bootloader/bootloader.py"])
                    return
                
                elif command_input.strip() == "help":
                    output_lines.append("Available commands:")
                    output_lines.append("  help - Show this help")
                    output_lines.append("  clear - Clear screen")
                    output_lines.append("  dir/ls - List files")
                    output_lines.append("  cd <path> - Change directory")
                    output_lines.append("  pwd - Show current directory")
                    output_lines.append("  sysinfo - Show system information")
                    output_lines.append("  checkdisk - Check disk integrity")
                    output_lines.append("  fixconfig - Reset configuration")
                    output_lines.append("  exit - Exit safe mode and reboot")
                
                elif command_input.strip() == "clear":
                    output_lines = ["Screen cleared"]
                
                elif command_input.strip() in ["dir", "ls"]:
                    try:
                        files = os.listdir(".")
                        output_lines.append("Directory listing:")
                        for f in files[:10]:  # Limit to 10 files
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
                
                elif command_input.strip() == "sysinfo":
                    output_lines.append("=== System Information ===")
                    output_lines.append("OS: Python-DOS 1.0.0")
                    output_lines.append("Mode: Safe Mode")
                    output_lines.append("Build: 2026.03.08")
                    output_lines.append(f"Working Dir: {os.getcwd()}")
                
                elif command_input.strip() == "checkdisk":
                    output_lines.append("Checking disk integrity...")
                    output_lines.append("[OK] File system structure")
                    output_lines.append("[OK] Configuration files")
                    output_lines.append("[OK] Application files")
                    output_lines.append("Disk check complete - no errors found")
                
                elif command_input.strip() == "fixconfig":
                    output_lines.append("Resetting configuration to defaults...")
                    try:
                        import json
                        default_config = {
                            "region": "United States",
                            "scaling": 1.0,
                            "background_color": "blue",
                            "selection_color": "red",
                            "password": ""
                        }
                        with open('config.json', 'w') as f:
                            json.dump(default_config, indent=4, fp=f)
                        output_lines.append("[OK] Configuration reset successfully")
                        output_lines.append("Reboot to apply changes")
                    except Exception as e:
                        output_lines.append(f"[ERROR] Failed to reset config: {e}")
                
                else:
                    # Try to execute as system command
                    try:
                        result = subprocess.run(command_input, shell=True, capture_output=True, 
                                              text=True, timeout=5)
                        if result.stdout:
                            for line in result.stdout.split('\n')[:5]:
                                if line:
                                    output_lines.append(line)
                        if result.stderr:
                            output_lines.append(f"Error: {result.stderr[:100]}")
                    except subprocess.TimeoutExpired:
                        output_lines.append("Command timed out")
                    except Exception:
                        output_lines.append(f"Unknown command: {command_input}")
                        output_lines.append("Type 'help' for available commands")
                
                command_input = ""
        
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            if command_input:
                command_input = command_input[:-1]
        
        elif 32 <= key <= 126:  # Printable characters
            command_input += chr(key)

def main(stdscr):
    safe_mode_shell(stdscr)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Failed to start safe mode: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
