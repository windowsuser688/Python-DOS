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

try:
    from pygame import mixer
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

def draw_window(stdscr, y, x, w, h, title, lines, selected=None):
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
            if selected is not None and i == selected:
                stdscr.addstr(y+1+i, x+2, line[:w-4], curses.color_pair(3))
            else:
                stdscr.addstr(y+1+i, x+2, line[:w-4], curses.color_pair(1))
    
    # Draw shadow
    stdscr.attron(curses.color_pair(4))
    for i in range(h):
        stdscr.addstr(y+i, x+w, " ")
    stdscr.addstr(y+h, x+1, " " * w)
    stdscr.attroff(curses.color_pair(4))

def music_player(stdscr):
    curses.curs_set(0)
    curses.start_color()
    init_colors()
    
    stdscr.bkgd(" ", curses.color_pair(5))
    stdscr.timeout(100)  # Non-blocking input
    
    if not PYGAME_AVAILABLE:
        while True:
            stdscr.clear()
            lines = [
                "ERROR: pygame not installed!",
                "",
                "Install with:",
                "pip install pygame",
                "",
                "Press ESC to exit"
            ]
            draw_window(stdscr, 5, 10, 50, 10, "Music Player", lines)
            stdscr.refresh()
            
            key = stdscr.getch()
            if key == 27:
                break
        return
    
    # Initialize mixer
    mixer.init()
    
    # Find MP3 files in current directory and subdirectories
    mp3_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                mp3_files.append(os.path.join(root, file))
    
    if not mp3_files:
        mp3_files = ["No music files found"]
    
    selected = 0
    scroll_offset = 0
    playing = False
    current_song = None
    paused = False
    
    while True:
        stdscr.clear()
        
        # Prepare display
        max_visible = 12
        visible_songs = mp3_files[scroll_offset:scroll_offset + max_visible]
        
        display_lines = []
        for i, song in enumerate(visible_songs):
            song_name = os.path.basename(song)
            if current_song == mp3_files[scroll_offset + i] and playing:
                prefix = "♪ " if not paused else "|| "
            else:
                prefix = "  "
            display_lines.append(f"{prefix}{song_name[:55]}")
        
        # Add controls
        controls = [
            "",
            "Controls:",
            "ENTER: Play | SPACE: Pause/Resume",
            "S: Stop | UP/DOWN: Navigate | ESC: Exit"
        ]
        
        all_lines = display_lines + controls
        
        draw_window(stdscr, 3, 5, 65, len(all_lines)+2, "Music Player", all_lines,
                   selected - scroll_offset if selected - scroll_offset < max_visible else None)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            mixer.music.stop()
            break
        
        elif key == curses.KEY_UP:
            if selected > 0:
                selected -= 1
                if selected < scroll_offset:
                    scroll_offset = selected
        
        elif key == curses.KEY_DOWN:
            if selected < len(mp3_files) - 1 and mp3_files[0] != "No music files found":
                selected += 1
                if selected >= scroll_offset + max_visible:
                    scroll_offset = selected - max_visible + 1
        
        elif key in [10, 13]:  # ENTER - Play
            if mp3_files[0] != "No music files found":
                try:
                    mixer.music.load(mp3_files[selected])
                    mixer.music.play()
                    current_song = mp3_files[selected]
                    playing = True
                    paused = False
                except Exception as e:
                    pass
        
        elif key == ord(' '):  # SPACE - Pause/Resume
            if playing:
                if paused:
                    mixer.music.unpause()
                    paused = False
                else:
                    mixer.music.pause()
                    paused = True
        
        elif key in [ord('s'), ord('S')]:  # Stop
            mixer.music.stop()
            playing = False
            paused = False
            current_song = None

def main(stdscr):
    music_player(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
