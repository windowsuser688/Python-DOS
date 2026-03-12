"""
Todo List App for Python-DOS
Manage your tasks with add, complete, and delete features
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

def draw_window(stdscr, y, x, w, h, title, lines, selected=None):
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
            if selected is not None and i == selected:
                stdscr.addstr(y+1+i, x+2, line[:w-4], curses.color_pair(3))
            else:
                stdscr.addstr(y+1+i, x+2, line[:w-4], curses.color_pair(1))
    
    stdscr.attron(curses.color_pair(4))
    for i in range(h):
        stdscr.addstr(y+i, x+w, " ")
    stdscr.addstr(y+h, x+1, " " * w)
    stdscr.attroff(curses.color_pair(4))

def get_input(stdscr, prompt):
    curses.curs_set(1)
    text = ""
    
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        height, width = stdscr.getmaxyx()
        lines = ["", prompt, "", text + "_", "", "ENTER: Confirm | ESC: Cancel"]
        
        draw_window(stdscr, height//2-4, width//2-25, 50, 10, "Input", lines)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:
            curses.curs_set(0)
            return None
        elif key in [10, 13]:
            curses.curs_set(0)
            return text if text else None
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            if text:
                text = text[:-1]
        elif 32 <= key <= 126 and len(text) < 40:
            text += chr(key)

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    init_colors()
    
    stdscr.bkgd(" ", curses.color_pair(5))
    
    todos = []
    selected = 0
    
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        lines = [f"=== Todo List ({len(todos)} tasks) ===", ""]
        
        if todos:
            for i, todo in enumerate(todos):
                status = "[X]" if todo['done'] else "[ ]"
                lines.append(f"{status} {todo['text']}")
        else:
            lines.append("No tasks yet!")
            lines.append("Press A to add a task")
        
        lines.extend([
            "",
            "A: Add | SPACE: Toggle | D: Delete",
            "UP/DOWN: Navigate | ESC: Exit"
        ])
        
        win_height = min(len(lines) + 4, height - 4)
        win_width = 60
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        draw_window(stdscr, win_y, win_x, win_width, win_height, "Todo List", lines, selected + 2 if todos else None)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            break
        elif key in [ord('a'), ord('A')]:
            task = get_input(stdscr, "Enter task:")
            if task:
                todos.append({'text': task, 'done': False})
                selected = len(todos) - 1
        elif key == ord(' ') and todos:
            todos[selected]['done'] = not todos[selected]['done']
        elif key in [ord('d'), ord('D')] and todos:
            todos.pop(selected)
            if selected >= len(todos) and todos:
                selected = len(todos) - 1
        elif key == curses.KEY_UP and todos:
            selected = (selected - 1) % len(todos)
        elif key == curses.KEY_DOWN and todos:
            selected = (selected + 1) % len(todos)

if __name__ == "__main__":
    curses.wrapper(main)
