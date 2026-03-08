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
            stdscr.addstr(y+1+i, x+2, line, curses.color_pair(1))
    
    # Draw shadow
    stdscr.attron(curses.color_pair(4))
    for i in range(h):
        stdscr.addstr(y+i, x+w, " ")
    stdscr.addstr(y+h, x+1, " " * w)
    stdscr.attroff(curses.color_pair(4))

def calculator(stdscr):
    curses.curs_set(0)
    curses.start_color()
    init_colors()
    
    stdscr.bkgd(" ", curses.color_pair(5))
    
    display = "0"
    current_input = ""
    operator = None
    previous = 0
    show_result = False
    
    while True:
        stdscr.clear()
        
        lines = [
            f"Display: {display[:30]}",
            "",
            "[7] [8] [9] [/]",
            "[4] [5] [6] [*]",
            "[1] [2] [3] [-]",
            "[0] [.] [=] [+]",
            "",
            "[C] Clear  [BACKSPACE] Delete",
            "",
            "ESC: Exit Calculator"
        ]
        
        draw_window(stdscr, 5, 10, 45, len(lines)+4, "Calculator", lines)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            break
        
        elif key in [ord('0'), ord('1'), ord('2'), ord('3'), ord('4'), 
                     ord('5'), ord('6'), ord('7'), ord('8'), ord('9')]:
            digit = chr(key)
            if show_result or display == "0":
                display = digit
                current_input = digit
                show_result = False
            else:
                display += digit
                current_input += digit
        
        elif key == ord('.'):
            if '.' not in current_input:
                if show_result or display == "0":
                    display = "0."
                    current_input = "0."
                    show_result = False
                else:
                    display += '.'
                    current_input += '.'
        
        elif key in [ord('+'), ord('-'), ord('*'), ord('/')]:
            try:
                if current_input:
                    previous = float(current_input)
                else:
                    previous = float(display)
                operator = chr(key)
                display += f" {operator} "
                current_input = ""
                show_result = False
            except:
                display = "Error"
                current_input = ""
                show_result = True
        
        elif key == ord('=') or key in [10, 13]:
            try:
                if current_input and operator:
                    current = float(current_input)
                    if operator == '+':
                        result = previous + current
                    elif operator == '-':
                        result = previous - current
                    elif operator == '*':
                        result = previous * current
                    elif operator == '/':
                        if current != 0:
                            result = previous / current
                        else:
                            display = "Error: Div by 0"
                            current_input = ""
                            show_result = True
                            continue
                    else:
                        continue
                    
                    if result == int(result):
                        display = str(int(result))
                    else:
                        display = str(round(result, 6))
                    current_input = display
                    operator = None
                    show_result = True
            except:
                display = "Error"
                current_input = ""
                show_result = True
        
        elif key in [ord('c'), ord('C')]:
            display = "0"
            current_input = ""
            operator = None
            previous = 0
            show_result = False
        
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            if len(display) > 1 and not show_result:
                display = display[:-1]
                if current_input:
                    current_input = current_input[:-1]
            else:
                display = "0"
                current_input = ""

def main(stdscr):
    calculator(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
