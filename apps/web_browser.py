try:
    import curses
except ImportError:
    print("ERROR: curses library not found!")
    print("Please install it with: pip install windows-curses")
    input("Press Enter to exit...")
    exit(1)

import urllib.request
import urllib.parse
import re
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from config_loader import load_config, init_colors
from html.parser import HTMLParser

class SimpleHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_content = []
        self.links = []
        self.current_link = None
        self.in_script = False
        self.in_style = False
        
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href':
                    self.current_link = value
        elif tag in ['script', 'style']:
            self.in_script = True
        elif tag == 'br':
            self.text_content.append("")
        elif tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if self.text_content and self.text_content[-1] != "":
                self.text_content.append("")
    
    def handle_endtag(self, tag):
        if tag == 'a':
            self.current_link = None
        elif tag in ['script', 'style']:
            self.in_script = False
        elif tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if self.text_content and self.text_content[-1] != "":
                self.text_content.append("")
    
    def handle_data(self, data):
        if self.in_script or self.in_style:
            return
            
        text = ' '.join(data.split())  # Normalize whitespace
        if text:
            if self.current_link:
                self.links.append((text, self.current_link))
                self.text_content.append(f"[LINK] {text}")
            else:
                self.text_content.append(text)

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

def fetch_url(url):
    """Fetch and parse a URL"""
    try:
        # Add http:// if no protocol specified
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        # Fetch the page
        headers = {'User-Agent': 'Python-DOS-Browser/1.0'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        # Parse HTML
        parser = SimpleHTMLParser()
        parser.feed(html)
        
        # Clean up content - remove empty lines and limit line length
        cleaned_content = []
        for line in parser.text_content:
            if line.strip():
                # Wrap long lines
                while len(line) > 65:
                    cleaned_content.append(line[:65])
                    line = line[65:]
                if line:
                    cleaned_content.append(line)
        
        return cleaned_content[:200], parser.links, None  # Limit to 200 lines
    
    except Exception as e:
        return [f"Error loading page: {str(e)}"], [], str(e)

def web_browser(stdscr):
    curses.curs_set(0)
    curses.start_color()
    init_colors()
    
    stdscr.bkgd(" ", curses.color_pair(5))
    
    current_url = ""
    page_content = ["Welcome to Python-DOS Browser!", "", "Enter a URL to browse", "", 
                   "Try: example.com", "     python.org", "     wikipedia.org"]
    links = []
    scroll_offset = 0
    history = []
    
    while True:
        stdscr.clear()
        
        # Prepare display
        max_visible = 16
        visible_content = page_content[scroll_offset:scroll_offset + max_visible]
        
        # Add address bar and controls
        header = [
            f"URL: {current_url[:60]}",
            "=" * 68,
            ""
        ]
        
        footer = [
            "",
            "G: Go to URL | B: Back | R: Refresh | ESC: Exit",
            "UP/DOWN: Scroll"
        ]
        
        all_lines = header + visible_content + footer
        
        draw_window(stdscr, 2, 3, 72, len(all_lines)+2, "Web Browser", all_lines)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            break
        
        elif key == curses.KEY_UP:
            if scroll_offset > 0:
                scroll_offset -= 1
        
        elif key == curses.KEY_DOWN:
            if scroll_offset < len(page_content) - max_visible:
                scroll_offset += 1
        
        elif key in [ord('g'), ord('G')]:  # Go to URL
            new_url = get_url_input(stdscr)
            if new_url:
                stdscr.clear()
                stdscr.bkgd(" ", curses.color_pair(5))
                loading_msg = ["Loading...", "", f"Fetching: {new_url}"]
                draw_window(stdscr, 10, 15, 50, 7, "Loading", loading_msg)
                stdscr.refresh()
                
                content, new_links, error = fetch_url(new_url)
                
                if not error:
                    history.append(current_url)
                    current_url = new_url
                    page_content = content
                    links = new_links
                    scroll_offset = 0
                else:
                    page_content = [f"Failed to load: {new_url}", "", f"Error: {error}"]
        
        elif key in [ord('b'), ord('B')]:  # Back
            if history:
                prev_url = history.pop()
                if prev_url:
                    content, new_links, error = fetch_url(prev_url)
                    if not error:
                        current_url = prev_url
                        page_content = content
                        links = new_links
                        scroll_offset = 0
        
        elif key in [ord('r'), ord('R')]:  # Refresh
            if current_url:
                stdscr.clear()
                stdscr.bkgd(" ", curses.color_pair(5))
                loading_msg = ["Refreshing...", "", f"Fetching: {current_url}"]
                draw_window(stdscr, 10, 15, 50, 7, "Loading", loading_msg)
                stdscr.refresh()
                
                content, new_links, error = fetch_url(current_url)
                
                if not error:
                    page_content = content
                    links = new_links
                    scroll_offset = 0

def get_url_input(stdscr):
    """Get URL input from user"""
    curses.curs_set(1)
    url = ""
    
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        # Draw input box
        for i in range(7):
            stdscr.addstr(10+i, 15, " " * 50, curses.color_pair(1))
        
        stdscr.addstr(11, 17, "Enter URL:", curses.color_pair(1))
        stdscr.addstr(12, 17, url[:45], curses.color_pair(1))
        stdscr.addstr(14, 17, "ENTER: Go | ESC: Cancel", curses.color_pair(1))
        
        stdscr.move(12, 17 + len(url[:45]))
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            curses.curs_set(0)
            return None
        elif key in [10, 13]:  # ENTER
            curses.curs_set(0)
            return url if url else None
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            if url:
                url = url[:-1]
        elif 32 <= key <= 126:
            url += chr(key)

def main(stdscr):
    web_browser(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
