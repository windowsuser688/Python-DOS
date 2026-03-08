try:
    import curses
except ImportError:
    print("ERROR: curses library not found!")
    print("Please install it with: pip install windows-curses")
    input("Press Enter to exit...")
    exit(1)

import subprocess
import os
import json

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

def single_user_shell(stdscr):
    curses.curs_set(1)
    curses.start_color()
    
    # Single user mode colors
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    
    stdscr.bkgd(" ", curses.color_pair(1))
    
    output_lines = [
        "Python-DOS Single User Mode",
        "WARNING: Administrative access only",
        "All services disabled - root shell",
        "",
        "Type 'help' for commands, 'exit' to reboot",
        ""
    ]
    command_input = ""
    
    while True:
        stdscr.clear()
        
        # Show warning banner
        height, width = stdscr.getmaxyx()
        banner = "*** SINGLE USER MODE ***"
        stdscr.addstr(1, (width - len(banner)) // 2, banner, curses.color_pair(5) | curses.A_BOLD)
        
        # Prepare display
        display_lines = output_lines[-13:] + [f"root# {command_input}"]
        
        draw_window(stdscr, 3, 5, 70, 18, "Single User Shell", display_lines)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            break
        
        elif key in [10, 13]:  # ENTER
            if command_input.strip():
                output_lines.append(f"root# {command_input}")
                
                if command_input.strip() == "exit":
                    output_lines.append("Rebooting to multi-user mode...")
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
                    output_lines.append("Single User Mode Commands:")
                    output_lines.append("  help - Show this help")
                    output_lines.append("  clear - Clear screen")
                    output_lines.append("  users - List all users")
                    output_lines.append("  resetpwd <user> - Reset user password")
                    output_lines.append("  sysinfo - Show system information")
                    output_lines.append("  fsck - File system check")
                    output_lines.append("  mount - Show mounted filesystems")
                    output_lines.append("  exit - Exit and reboot")
                
                elif command_input.strip() == "clear":
                    output_lines = ["Screen cleared"]
                
                elif command_input.strip() == "users":
                    try:
                        with open('config.json', 'r') as f:
                            config = json.load(f)
                        users = config.get('users', [])
                        output_lines.append("System Users:")
                        for user in users:
                            has_pwd = "Yes" if user.get('password') else "No"
                            output_lines.append(f"  {user['username']} (Password: {has_pwd})")
                    except Exception as e:
                        output_lines.append(f"Error: {e}")
                
                elif command_input.strip().startswith("resetpwd "):
                    username = command_input.strip()[9:]
                    try:
                        with open('config.json', 'r') as f:
                            config = json.load(f)
                        users = config.get('users', [])
                        found = False
                        for user in users:
                            if user['username'] == username:
                                user['password'] = ''
                                found = True
                                break
                        if found:
                            config['users'] = users
                            with open('config.json', 'w') as f:
                                json.dump(config, indent=4, fp=f)
                            output_lines.append(f"Password reset for user '{username}'")
                        else:
                            output_lines.append(f"User '{username}' not found")
                    except Exception as e:
                        output_lines.append(f"Error: {e}")
                
                elif command_input.strip() == "sysinfo":
                    output_lines.append("=== System Information ===")
                    output_lines.append("OS: Python-DOS 1.0.0")
                    output_lines.append("Mode: Single User Mode")
                    output_lines.append("User: root (UID 0)")
                    output_lines.append(f"Working Dir: {os.getcwd()}")
                
                elif command_input.strip() == "fsck":
                    output_lines.append("Checking file system...")
                    output_lines.append("[OK] /usr/root/Documents")
                    output_lines.append("[OK] /usr/root/Downloads")
                    output_lines.append("[OK] /apps")
                    output_lines.append("[OK] /bootloader")
                    output_lines.append("File system check complete")
                
                elif command_input.strip() == "mount":
                    output_lines.append("Mounted filesystems:")
                    output_lines.append("  /usr/root/Documents")
                    output_lines.append("  /usr/root/Downloads")
                    output_lines.append("  /apps")
                    output_lines.append("  /bootloader")
                    output_lines.append("  /safemode")
                    output_lines.append("  /verbosemode")
                    output_lines.append("  /singleusermode")
                
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
        
        elif 32 <= key <= 126:
            command_input += chr(key)

def main(stdscr):
    single_user_shell(stdscr)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Failed to start single user mode: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
