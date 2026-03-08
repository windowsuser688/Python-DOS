try:
    import curses
except ImportError:
    print("ERROR: curses library not found!")
    print("Please install it with: pip install windows-curses")
    input("Press Enter to exit...")
    exit(1)

from datetime import datetime, timedelta
import json
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from config_loader import init_colors

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

def save_config(config):
    """Save configuration to config.json"""
    try:
        with open('config.json', 'w') as f:
            json.dump(config, indent=4, fp=f)
        return True
    except:
        return False

def get_timezone_offset(region):
    """Get timezone offset in hours based on region"""
    offsets = {
        "United States": -5,
        "United Kingdom": 0,
        "Canada": -5,
        "Mexico": -6,
        "Brazil": -3,
        "Argentina": -3,
        "France": 1,
        "Germany": 1,
        "Italy": 1,
        "Spain": 1,
        "Russia": 3,
        "China": 8,
        "Japan": 9,
        "South Korea": 9,
        "India": 5.5,
        "Australia": 10,
        "New Zealand": 12,
        "South Africa": 2,
        "Egypt": 2,
        "Nigeria": 1,
        "Kenya": 3,
        "Saudi Arabia": 3,
        "UAE": 4,
        "Turkey": 3,
        "Greece": 2,
        "Poland": 1,
        "Netherlands": 1,
        "Belgium": 1,
        "Sweden": 1,
        "Norway": 1,
        "Denmark": 1,
        "Finland": 2,
        "Switzerland": 1,
        "Austria": 1,
        "Portugal": 0,
        "Ireland": 0,
        "Iceland": 0,
        "Ukraine": 2,
        "Romania": 2,
        "Czech Republic": 1,
        "Hungary": 1,
        "Bulgaria": 2,
        "Serbia": 1,
        "Croatia": 1,
        "Slovakia": 1,
        "Lithuania": 2,
        "Latvia": 2,
        "Estonia": 2,
        "Slovenia": 1,
        "Luxembourg": 1,
        "Malta": 1,
        "Cyprus": 2,
        "Israel": 2,
        "Jordan": 2,
        "Lebanon": 2,
        "Syria": 2,
        "Iraq": 3,
        "Iran": 3.5,
        "Afghanistan": 4.5,
        "Pakistan": 5,
        "Bangladesh": 6,
        "Sri Lanka": 5.5,
        "Nepal": 5.75,
        "Myanmar": 6.5,
        "Thailand": 7,
        "Vietnam": 7,
        "Cambodia": 7,
        "Laos": 7,
        "Malaysia": 8,
        "Singapore": 8,
        "Indonesia": 7,
        "Philippines": 8,
        "Taiwan": 8,
        "Hong Kong": 8,
        "Mongolia": 8,
        "North Korea": 9,
        "Brunei": 8,
        "Timor-Leste": 9,
        "Papua New Guinea": 10,
        "Fiji": 12,
        "Solomon Islands": 11,
        "Vanuatu": 11,
        "Samoa": 13,
        "Tonga": 13,
        "Chile": -4,
        "Peru": -5,
        "Colombia": -5,
        "Venezuela": -4,
        "Ecuador": -5,
        "Bolivia": -4,
        "Paraguay": -4,
        "Uruguay": -3,
        "Guyana": -4,
        "Suriname": -3,
        "French Guiana": -3,
        "Panama": -5,
        "Costa Rica": -6,
        "Nicaragua": -6,
        "Honduras": -6,
        "El Salvador": -6,
        "Guatemala": -6,
        "Belize": -6,
        "Jamaica": -5,
        "Cuba": -5,
        "Haiti": -5,
        "Dominican Republic": -4,
        "Puerto Rico": -4,
        "Trinidad and Tobago": -4,
        "Barbados": -4,
        "Bahamas": -5,
        "Greenland": -3,
        "Morocco": 0,
        "Algeria": 1,
        "Tunisia": 1,
        "Libya": 2,
        "Sudan": 2,
        "Ethiopia": 3,
        "Somalia": 3,
        "Tanzania": 3,
        "Uganda": 3,
        "Rwanda": 2,
        "Burundi": 2,
        "Zambia": 2,
        "Zimbabwe": 2,
        "Mozambique": 2,
        "Malawi": 2,
        "Botswana": 2,
        "Namibia": 2,
        "Angola": 1,
        "Ghana": 0,
        "Ivory Coast": 0,
        "Senegal": 0,
        "Mali": 0,
        "Burkina Faso": 0,
        "Niger": 1,
        "Chad": 1,
        "Cameroon": 1,
        "Central African Republic": 1,
        "Congo": 1,
        "DR Congo": 1,
        "Gabon": 1,
        "Equatorial Guinea": 1,
        "Benin": 1,
        "Togo": 0,
        "Liberia": 0,
        "Sierra Leone": 0,
        "Guinea": 0,
        "Gambia": 0,
        "Guinea-Bissau": 0,
        "Mauritania": 0,
        "Madagascar": 3,
        "Mauritius": 4,
        "Seychelles": 4,
        "Comoros": 3,
        "Djibouti": 3,
        "Eritrea": 3,
        "Lesotho": 2,
        "Eswatini": 2,
        "Cape Verde": -1,
        "Sao Tome and Principe": 0,
        "Oman": 4,
        "Yemen": 3,
        "Kuwait": 3,
        "Bahrain": 3,
        "Qatar": 3,
        "Kazakhstan": 6,
        "Uzbekistan": 5,
        "Turkmenistan": 5,
        "Kyrgyzstan": 6,
        "Tajikistan": 5,
        "Azerbaijan": 4,
        "Armenia": 4,
        "Georgia": 4,
        "Belarus": 3,
        "Moldova": 2,
        "Albania": 1,
        "North Macedonia": 1,
        "Bosnia and Herzegovina": 1,
        "Montenegro": 1,
        "Kosovo": 1,
        "Andorra": 1,
        "Monaco": 1,
        "San Marino": 1,
        "Vatican City": 1,
        "Liechtenstein": 1,
        "Maldives": 5,
        "Bhutan": 6
    }
    return offsets.get(region, 0)

def get_current_time(region):
    """Get current time adjusted for region"""
    offset = get_timezone_offset(region)
    utc_time = datetime.utcnow()
    local_time = utc_time + timedelta(hours=offset)
    return local_time.strftime("%Y-%m-%d %H:%M:%S")

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

def settings(stdscr):
    curses.curs_set(0)
    curses.start_color()
    init_colors()
    
    stdscr.bkgd(" ", curses.color_pair(5))
    
    config = load_config()
    menu_items = [
        "System Information",
        "Change Region",
        "Change Scaling",
        "Change Background Color",
        "Change Selection Color",
        "User Management",
        "Set Password",
        "Remove Password",
        "Save & Exit"
    ]
    selected = 0
    
    while True:
        stdscr.clear()
        
        current_time = get_current_time(config.get('region', 'United States'))
        term_size = stdscr.getmaxyx()
        
        lines = [
            "=== Settings Menu ===",
            ""
        ]
        
        for i, item in enumerate(menu_items):
            lines.append(item)
        
        lines.extend([
            "",
            "=== Current Settings ===",
            f"Region: {config.get('region', 'United States')}",
            f"Scaling: {config['scaling']}x",
            f"Background: {config['background_color']}",
            f"Selection: {config['selection_color']}",
            f"Current User: {config.get('current_user', 'root')}",
            f"Total Users: {len(config.get('users', []))}",
            "",
            "UP/DOWN: Navigate | ENTER: Select | ESC: Exit"
        ])
        
        draw_window(stdscr, 3, 5, 60, len(lines)+2, "Settings", lines, selected + 2)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            break
        
        elif key == curses.KEY_UP:
            selected = (selected - 1) % len(menu_items)
        
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(menu_items)
        
        elif key in [10, 13]:  # ENTER
            choice = menu_items[selected]
            
            if choice == "System Information":
                show_system_info(stdscr)
            
            elif choice == "Change Region":
                regions = ["United States", "United Kingdom", "Canada", "Mexico", "Brazil", "Argentina",
                          "France", "Germany", "Italy", "Spain", "Russia", "China", "Japan", "South Korea",
                          "India", "Australia", "New Zealand", "South Africa", "Egypt", "Nigeria"]
                new_region = show_selection_menu(stdscr, "Select Region (20 of 195)", regions)
                if new_region:
                    config['region'] = new_region
            
            elif choice == "Change Scaling":
                scales = ["0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"]
                new_scale = show_selection_menu(stdscr, "Select Scaling", scales)
                if new_scale:
                    config['scaling'] = float(new_scale.replace('x', ''))
            
            elif choice == "Change Background Color":
                colors = ["blue", "black", "cyan", "green", "magenta"]
                new_color = show_selection_menu(stdscr, "Select Background Color", colors)
                if new_color:
                    config['background_color'] = new_color
            
            elif choice == "Change Selection Color":
                colors = ["red", "yellow", "green", "cyan", "magenta", "white"]
                new_color = show_selection_menu(stdscr, "Select Selection Color", colors)
                if new_color:
                    config['selection_color'] = new_color
            
            elif choice == "User Management":
                user_management(stdscr, config)
            
            elif choice == "Set Password":
                # Get current user
                current_user = config.get('current_user', 'root')
                users = config.get('users', [{'username': 'root', 'password': '', 'home_dir': 'usr/root'}])
                
                new_password = get_password_input_settings(stdscr, "Set Password: ")
                if new_password:
                    confirm_password = get_password_input_settings(stdscr, "Confirm Password: ")
                    if new_password == confirm_password:
                        # Update password for current user
                        for user in users:
                            if user['username'] == current_user:
                                user['password'] = new_password
                                break
                        config['users'] = users
                        show_message(stdscr, "Password set successfully!")
                    else:
                        show_message(stdscr, "Passwords do not match!")
            
            elif choice == "Remove Password":
                # Get current user
                current_user = config.get('current_user', 'root')
                users = config.get('users', [{'username': 'root', 'password': '', 'home_dir': 'usr/root'}])
                
                # Check if current user has password
                has_password = False
                for user in users:
                    if user['username'] == current_user and user.get('password'):
                        has_password = True
                        break
                
                if has_password:
                    confirm = confirm_dialog(stdscr, "Remove password protection?")
                    if confirm:
                        for user in users:
                            if user['username'] == current_user:
                                user['password'] = ''
                                break
                        config['users'] = users
                        show_message(stdscr, "Password removed!")
                else:
                    show_message(stdscr, "No password is set!")
            
            elif choice == "Save & Exit":
                if save_config(config):
                    show_message(stdscr, "Settings saved successfully!")
                else:
                    show_message(stdscr, "Failed to save settings!")
                break

def show_system_info(stdscr):
    """Show system information screen"""
    config = load_config()
    
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        current_time = get_current_time(config.get('region', 'United States'))
        term_size = stdscr.getmaxyx()
        
        lines = [
            "=== System Information ===",
            "",
            "OS Name: Python-DOS",
            "Version: 1.0.0",
            "Build: 2026.03.08",
            "",
            f"Region: {config.get('region', 'United States')}",
            f"Current Time: {current_time}",
            f"Terminal Size: {term_size[0]}x{term_size[1]}",
            "",
            "Press ESC to go back"
        ]
        
        draw_window(stdscr, 5, 10, 50, len(lines)+2, "System Information", lines)
        stdscr.refresh()
        
        key = stdscr.getch()
        if key == 27:
            break

def show_selection_menu(stdscr, title, options):
    """Show a selection menu and return the selected option"""
    selected = 0
    
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        lines = []
        for opt in options:
            lines.append(opt)
        
        lines.append("")
        lines.append("UP/DOWN: Navigate | ENTER: Select | ESC: Cancel")
        
        draw_window(stdscr, 8, 15, 40, len(lines)+2, title, lines, selected)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            return None
        elif key == curses.KEY_UP:
            selected = (selected - 1) % len(options)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)
        elif key in [10, 13]:  # ENTER
            return options[selected]

def show_message(stdscr, message):
    """Show a message dialog"""
    stdscr.clear()
    stdscr.bkgd(" ", curses.color_pair(5))
    
    lines = [message, "", "Press any key to continue"]
    draw_window(stdscr, 10, 20, 40, 6, "Message", lines)
    stdscr.refresh()
    stdscr.getch()

def get_password_input_settings(stdscr, prompt):
    """Get password input for settings"""
    curses.curs_set(1)
    password = ""
    
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        # Draw input box
        for i in range(9):
            stdscr.addstr(9+i, 15, " " * 55, curses.color_pair(1))
        
        stdscr.addstr(10, 17, prompt, curses.color_pair(1))
        stdscr.addstr(11, 17, "*" * len(password), curses.color_pair(1))
        stdscr.addstr(13, 17, "Password will be hidden with asterisks", curses.color_pair(1))
        stdscr.addstr(14, 17, "ENTER: Confirm | ESC: Cancel", curses.color_pair(1))
        
        stdscr.move(11, 17 + len(password))
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            curses.curs_set(0)
            return None
        elif key in [10, 13]:  # ENTER
            curses.curs_set(0)
            return password if password else None
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            if password:
                password = password[:-1]
        elif 32 <= key <= 126:
            password += chr(key)

def user_management(stdscr, config):
    """User management menu"""
    while True:
        users = config.get('users', [])
        menu_items = ["Add User", "Delete User", "List Users", "Back"]
        selected = 0
        
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        height, width = stdscr.getmaxyx()
        
        lines = []
        for item in menu_items:
            lines.append(item)
        
        lines.append("")
        lines.append(f"Total Users: {len(users)}")
        
        win_height = len(lines) + 4
        win_width = 40
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        draw_window(stdscr, win_y, win_x, win_width, win_height, "User Management", lines, selected)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            return
        elif key == curses.KEY_UP:
            selected = (selected - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(menu_items)
        elif key in [10, 13]:
            choice = menu_items[selected]
            
            if choice == "Add User":
                username = get_text_input(stdscr, "Enter username: ")
                if username:
                    # Check if user exists
                    exists = any(u['username'] == username for u in users)
                    if exists:
                        show_message(stdscr, "User already exists!")
                    else:
                        # Create user directory
                        import os
                        home_dir = f"usr/{username}"
                        try:
                            os.makedirs(f"{home_dir}/Documents", exist_ok=True)
                            os.makedirs(f"{home_dir}/Downloads", exist_ok=True)
                            users.append({
                                'username': username,
                                'password': '',
                                'home_dir': home_dir
                            })
                            config['users'] = users
                            show_message(stdscr, f"User '{username}' created!")
                        except Exception as e:
                            show_message(stdscr, f"Error: {e}")
            
            elif choice == "Delete User":
                if len(users) <= 1:
                    show_message(stdscr, "Cannot delete the last user!")
                else:
                    usernames = [u['username'] for u in users if u['username'] != 'root']
                    if not usernames:
                        show_message(stdscr, "No users to delete (root cannot be deleted)")
                    else:
                        user_to_delete = show_selection_menu(stdscr, "Select user to delete", usernames)
                        if user_to_delete:
                            confirm = confirm_dialog(stdscr, f"Delete user '{user_to_delete}'?")
                            if confirm:
                                users = [u for u in users if u['username'] != user_to_delete]
                                config['users'] = users
                                show_message(stdscr, f"User '{user_to_delete}' deleted!")
            
            elif choice == "List Users":
                user_list = []
                for user in users:
                    has_pwd = "Yes" if user.get('password') else "No"
                    user_list.append(f"{user['username']} (Password: {has_pwd})")
                user_list.append("")
                user_list.append("Press any key to continue")
                
                draw_window(stdscr, win_y, win_x, 50, len(user_list)+4, "User List", user_list)
                stdscr.refresh()
                stdscr.getch()
            
            elif choice == "Back":
                return

def get_text_input(stdscr, prompt):
    """Get text input from user"""
    curses.curs_set(1)
    text = ""
    
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        for i in range(7):
            stdscr.addstr(10+i, 20, " " * 45, curses.color_pair(1))
        
        stdscr.addstr(11, 22, prompt, curses.color_pair(1))
        stdscr.addstr(12, 22, text[:40], curses.color_pair(1))
        stdscr.addstr(14, 22, "ENTER: Confirm | ESC: Cancel", curses.color_pair(1))
        
        stdscr.move(12, 22 + len(text[:40]))
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
        elif 32 <= key <= 126:
            text += chr(key)

def confirm_dialog(stdscr, message):
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        for i in range(6):
            stdscr.addstr(10+i, 20, " " * 45, curses.color_pair(1))
        
        stdscr.addstr(11, 22, message, curses.color_pair(1))
        stdscr.addstr(13, 22, "Y: Yes | N: No", curses.color_pair(1))
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key in [ord('y'), ord('Y')]:
            return True
        elif key in [ord('n'), ord('N'), 27]:
            return False

def main(stdscr):
    settings(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
