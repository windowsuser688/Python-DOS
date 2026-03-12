"""
Paint App for Python-DOS
Draw ASCII art with different characters and colors
Press S to save your artwork
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

def save_canvas(canvas, canvas_colors, filename):
    """Save canvas to file"""
    try:
        # Get current user
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        current_user = config.get('current_user', 'root')
        
        # Save to user's Documents folder
        save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               f'usr/{current_user}/Documents')
        os.makedirs(save_dir, exist_ok=True)
        
        filepath = os.path.join(save_dir, filename + '.txt')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for row in canvas:
                f.write(''.join(row) + '\n')
        
        return True
    except:
        return False

def get_filename(stdscr):
    """Get filename from user"""
    curses.curs_set(1)
    text = ""
    
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        height, width = stdscr.getmaxyx()
        
        # Draw input box
        for i in range(9):
            stdscr.addstr(height//2 - 4 + i, width//2 - 25, " " * 50, curses.color_pair(1))
        
        stdscr.addstr(height//2 - 2, width//2 - 20, "Save as:", curses.color_pair(1))
        stdscr.addstr(height//2, width//2 - 20, text + "_", curses.color_pair(1))
        stdscr.addstr(height//2 + 2, width//2 - 20, "ENTER: Save | ESC: Cancel", curses.color_pair(1))
        
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
        elif 32 <= key <= 126 and len(text) < 30:
            char = chr(key)
            if char.isalnum() or char in ['_', '-']:
                text += char

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    init_colors()
    
    # Initialize color pairs for painting
    curses.init_pair(10, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(11, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(12, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(13, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(14, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(15, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(16, curses.COLOR_WHITE, curses.COLOR_BLACK)
    
    stdscr.bkgd(" ", curses.color_pair(5))
    
    height, width = stdscr.getmaxyx()
    
    # Canvas setup
    canvas_height = height - 6
    canvas_width = width - 4
    canvas = [[' ' for _ in range(canvas_width)] for _ in range(canvas_height)]
    canvas_colors = [[16 for _ in range(canvas_width)] for _ in range(canvas_height)]
    
    cursor_y = canvas_height // 2
    cursor_x = canvas_width // 2
    
    brushes = ['█', '▓', '▒', '░', '#', '*', '+', '.', 'O']
    current_brush = 0
    current_color = 16
    
    colors = [
        ('Red', 10), ('Green', 11), ('Yellow', 12), ('Blue', 13),
        ('Magenta', 14), ('Cyan', 15), ('White', 16)
    ]
    color_index = 6
    
    while True:
        stdscr.clear()
        
        # Draw canvas border
        for i in range(canvas_height + 2):
            stdscr.addstr(i + 1, 1, "│", curses.color_pair(2))
            stdscr.addstr(i + 1, canvas_width + 2, "│", curses.color_pair(2))
        
        stdscr.addstr(1, 1, "┌" + "─" * canvas_width + "┐", curses.color_pair(2))
        stdscr.addstr(canvas_height + 2, 1, "└" + "─" * canvas_width + "┘", curses.color_pair(2))
        
        # Draw canvas
        for y in range(canvas_height):
            for x in range(canvas_width):
                try:
                    stdscr.addstr(y + 2, x + 2, canvas[y][x], curses.color_pair(canvas_colors[y][x]))
                except:
                    pass
        
        # Draw cursor
        try:
            stdscr.addstr(cursor_y + 2, cursor_x + 2, brushes[current_brush], 
                         curses.color_pair(current_color) | curses.A_REVERSE)
        except:
            pass
        
        # Draw toolbar
        toolbar_y = height - 3
        toolbar = f"Brush: {brushes[current_brush]} | Color: {colors[color_index][0]} | SPACE:Draw | B:Brush | C:Color | S:Save | X:Clear | ESC:Exit"
        try:
            stdscr.addstr(toolbar_y, 2, toolbar[:width-4], curses.color_pair(1))
        except:
            pass
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            break
        elif key == curses.KEY_UP and cursor_y > 0:
            cursor_y -= 1
        elif key == curses.KEY_DOWN and cursor_y < canvas_height - 1:
            cursor_y += 1
        elif key == curses.KEY_LEFT and cursor_x > 0:
            cursor_x -= 1
        elif key == curses.KEY_RIGHT and cursor_x < canvas_width - 1:
            cursor_x += 1
        elif key == ord(' '):  # Draw
            canvas[cursor_y][cursor_x] = brushes[current_brush]
            canvas_colors[cursor_y][cursor_x] = current_color
        elif key in [ord('b'), ord('B')]:  # Change brush
            current_brush = (current_brush + 1) % len(brushes)
        elif key in [ord('c'), ord('C')]:  # Change color
            color_index = (color_index + 1) % len(colors)
            current_color = colors[color_index][1]
        elif key in [ord('s'), ord('S')]:  # Save
            filename = get_filename(stdscr)
            if filename:
                if save_canvas(canvas, canvas_colors, filename):
                    # Show success message briefly
                    try:
                        stdscr.addstr(toolbar_y, 2, f"Saved as {filename}.txt!" + " " * 50, curses.color_pair(3))
                        stdscr.refresh()
                        stdscr.nodelay(1)
                        stdscr.timeout(1000)
                        stdscr.getch()
                        stdscr.nodelay(0)
                        stdscr.timeout(-1)
                    except:
                        pass
        elif key in [ord('x'), ord('X')]:  # Clear canvas
            canvas = [[' ' for _ in range(canvas_width)] for _ in range(canvas_height)]
            canvas_colors = [[16 for _ in range(canvas_width)] for _ in range(canvas_height)]

if __name__ == "__main__":
    curses.wrapper(main)
