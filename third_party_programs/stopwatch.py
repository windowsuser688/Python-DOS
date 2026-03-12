"""
Stopwatch App for Python-DOS
Track time with start, stop, and lap features
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
import time

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

def draw_window(stdscr, y, x, w, h, title, lines):
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
            stdscr.addstr(y+1+i, x+2, line[:w-4], curses.color_pair(1))
    
    stdscr.attron(curses.color_pair(4))
    for i in range(h):
        stdscr.addstr(y+i, x+w, " ")
    stdscr.addstr(y+h, x+1, " " * w)
    stdscr.attroff(curses.color_pair(4))

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 100)
    return f"{mins:02d}:{secs:02d}.{millis:02d}"

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    init_colors()
    
    stdscr.bkgd(" ", curses.color_pair(5))
    stdscr.nodelay(1)
    stdscr.timeout(50)
    
    running = False
    start_time = 0
    elapsed = 0
    laps = []
    
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Update elapsed time if running
        if running:
            elapsed = time.time() - start_time
        
        lines = [
            "",
            f"Time: {format_time(elapsed)}",
            "",
            "=== Laps ===",
            ""
        ]
        
        if laps:
            for i, lap in enumerate(laps[-5:], 1):
                lines.append(f"Lap {len(laps) - 5 + i}: {format_time(lap)}")
        else:
            lines.append("No laps recorded")
        
        lines.extend([
            "",
            "SPACE: Start/Stop",
            "L: Lap | R: Reset",
            "ESC: Exit"
        ])
        
        win_height = len(lines) + 4
        win_width = 50
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        status = "RUNNING" if running else "STOPPED"
        draw_window(stdscr, win_y, win_x, win_width, win_height, f"Stopwatch - {status}", lines)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            break
        elif key == ord(' '):  # Start/Stop
            if running:
                running = False
            else:
                start_time = time.time() - elapsed
                running = True
        elif key in [ord('l'), ord('L')] and running:  # Lap
            laps.append(elapsed)
        elif key in [ord('r'), ord('R')]:  # Reset
            running = False
            elapsed = 0
            laps = []

if __name__ == "__main__":
    curses.wrapper(main)
