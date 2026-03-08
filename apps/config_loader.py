"""Shared configuration loader for all apps"""
import json
import curses

def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except:
        return {
            "region": "United States",
            "scaling": 1.0,
            "background_color": "blue",
            "selection_color": "red"
        }

def get_color_code(color_name):
    """Convert color name to curses color code"""
    color_map = {
        "black": curses.COLOR_BLACK,
        "red": curses.COLOR_RED,
        "green": curses.COLOR_GREEN,
        "yellow": curses.COLOR_YELLOW,
        "blue": curses.COLOR_BLUE,
        "magenta": curses.COLOR_MAGENTA,
        "cyan": curses.COLOR_CYAN,
        "white": curses.COLOR_WHITE
    }
    return color_map.get(color_name.lower(), curses.COLOR_BLUE)

def init_colors():
    """Initialize color pairs based on config"""
    config = load_config()
    bg_color = get_color_code(config.get('background_color', 'blue'))
    sel_color = get_color_code(config.get('selection_color', 'red'))
    
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)   # window fill
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)   # borders
    curses.init_pair(3, curses.COLOR_WHITE, sel_color)            # selection
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)   # shadow
    curses.init_pair(5, curses.COLOR_WHITE, bg_color)             # desktop bg
    
    return config
