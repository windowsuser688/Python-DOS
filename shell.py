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

# Set terminal type for simulated terminals
os.environ['TERM'] = 'xterm-256color'

def create_boot_log():
    """Create boot cache log with system details"""
    import datetime
    
    # Create boot_cache folder if it doesn't exist
    if not os.path.exists('boot_cache'):
        os.makedirs('boot_cache')
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"boot_cache/boot_{timestamp}.log"
    
    try:
        with open(log_file, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("Python-DOS Boot Log\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Boot Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Python Version: {sys.version}\n")
            f.write(f"Platform: {sys.platform}\n")
            f.write(f"Working Directory: {os.getcwd()}\n\n")
            
            f.write("=" * 60 + "\n")
            f.write("Configuration\n")
            f.write("=" * 60 + "\n\n")
            
            # Load and log config
            config = load_config()
            f.write(f"Background Color: {config.get('background_color', 'blue')}\n")
            f.write(f"Selection Color: {config.get('selection_color', 'red')}\n")
            f.write(f"Timezone Offset: {config.get('timezone_offset', 0)}\n")
            f.write(f"Scaling: {config.get('scaling', 1.0)}\n")
            f.write(f"Current User: {config.get('current_user', 'root')}\n")
            f.write(f"Total Users: {len(config.get('users', []))}\n\n")
            
            f.write("=" * 60 + "\n")
            f.write("System Files\n")
            f.write("=" * 60 + "\n\n")
            
            # Log key files
            key_files = ['shell.py', 'config.json', 'bootloader/bootloader.py']
            for file in key_files:
                if os.path.exists(file):
                    size = os.path.getsize(file)
                    f.write(f"{file}: {size} bytes\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("Boot Sequence Complete\n")
            f.write("=" * 60 + "\n")
    except:
        pass

def load_config():
    """Load configuration from config.json"""
    import json
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except:
        return {
            "timezone": "UTC",
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

def draw_window(stdscr, y, x, w, h, title, lines, selected=None, use_arrow=False):
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
                if use_arrow:
                    stdscr.addstr(y+1+i, x+2, "> " + line, curses.color_pair(3))
                else:
                    stdscr.addstr(y+1+i, x+2, line, curses.color_pair(3))
            else:
                if use_arrow:
                    stdscr.addstr(y+1+i, x+2, "  " + line, curses.color_pair(1))
                else:
                    stdscr.addstr(y+1+i, x+2, line, curses.color_pair(1))
    
    # Draw scrollbar if needed
    if len(lines) > h-2:
        scrollbar_height = h - 2
        thumb_size = max(1, int((h-2) / len(lines) * scrollbar_height))
        thumb_pos = int((selected or 0) / len(lines) * scrollbar_height) if selected is not None else 0
        
        for i in range(scrollbar_height):
            if thumb_pos <= i < thumb_pos + thumb_size:
                stdscr.addstr(y+1+i, x+w-2, "█", curses.color_pair(2))
            else:
                stdscr.addstr(y+1+i, x+w-2, "░", curses.color_pair(2))
    
    # Draw shadow
    stdscr.attron(curses.color_pair(4))
    for i in range(h):
        stdscr.addstr(y+i, x+w, " ")
    stdscr.addstr(y+h, x+1, " " * w)
    stdscr.attroff(curses.color_pair(4))

def validate_user_folders():
    """Validate and clean up user folders in usr/ directory"""
    import os
    import shutil
    
    try:
        # Load config to get valid users
        config = load_config()
        valid_users = [user['username'] for user in config.get('users', [])]
        users_list = config.get('users', [])
        config_modified = False
        
        # Check if usr directory exists
        if not os.path.exists('usr'):
            os.makedirs('usr')
        
        # Ensure root user exists
        has_root = any(user['username'] == 'root' for user in users_list)
        if not has_root:
            # Create root user
            users_list.append({
                'username': 'root',
                'password': '',
                'home_dir': 'usr/root'
            })
            config_modified = True
            # Create root directories
            os.makedirs('usr/root/Documents', exist_ok=True)
            os.makedirs('usr/root/Downloads', exist_ok=True)
        
        # Check if root folder exists
        if not os.path.exists('usr/root'):
            os.makedirs('usr/root/Documents', exist_ok=True)
            os.makedirs('usr/root/Downloads', exist_ok=True)
        
        # Get all folders in usr/
        usr_folders = [f for f in os.listdir('usr') if os.path.isdir(os.path.join('usr', f))]
        
        # Remove users from config if their folder doesn't exist
        users_to_remove = []
        for user in users_list:
            username = user['username']
            if username not in usr_folders and username != 'root':
                users_to_remove.append(user)
        
        if users_to_remove:
            for user in users_to_remove:
                users_list.remove(user)
            config_modified = True
        
        # Check folders in usr/
        for folder in usr_folders:
            folder_path = os.path.join('usr', folder)
            
            # Check if this folder corresponds to a valid user
            if folder not in valid_users:
                # Check if it has Documents and Downloads subdirectories
                has_documents = os.path.exists(os.path.join(folder_path, 'Documents'))
                has_downloads = os.path.exists(os.path.join(folder_path, 'Downloads'))
                
                if has_documents and has_downloads:
                    # Valid structure - add as a user to config
                    users_list.append({
                        'username': folder,
                        'password': '',
                        'home_dir': f'usr/{folder}'
                    })
                    config_modified = True
                else:
                    # Invalid user folder - delete it (unless it's root)
                    if folder != 'root':
                        try:
                            shutil.rmtree(folder_path)
                        except:
                            pass
        
        # Save config if we made changes
        if config_modified:
            config['users'] = users_list
            # Ensure current_user is valid
            current_user = config.get('current_user', 'root')
            if current_user not in [u['username'] for u in users_list]:
                config['current_user'] = 'root'
            save_config(config)
    except:
        pass

def boot_sequence(stdscr):
    """Show fake GRUB bootloader and boot messages"""
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)  # boot text
    curses.init_pair(7, curses.COLOR_GREEN, curses.COLOR_BLACK)  # OK text
    
    stdscr.clear()
    stdscr.bkgd(" ", curses.color_pair(6))
    
    boot_messages = [
        "GRUB loading...",
        "Loading Python-DOS...",
        "",
        "Starting system services...",
        "[ OK ] Started System Logging Service",
        "[ OK ] Started Network Manager",
        "[ OK ] Started User Manager",
        "[ OK ] Started File System Check",
        "[ OK ] Mounted /dev/sda1",
        "[ OK ] Started Terminal Service",
        "[ OK ] Started Display Manager",
        "[ OK ] Started Audio Service",
        "[ OK ] Reached target Multi-User System",
        "",
        "Python-DOS 1.0.0 (tty1)",
        "",
        "Starting environment...",
    ]
    
    import time
    y = 2
    
    for msg in boot_messages:
        if "[ OK ]" in msg:
            # Split the message to color only "OK"
            parts = msg.split("OK")
            stdscr.addstr(y, 2, parts[0], curses.color_pair(6))
            stdscr.addstr(y, 2 + len(parts[0]), "OK", curses.color_pair(7))
            stdscr.addstr(y, 2 + len(parts[0]) + 2, parts[1], curses.color_pair(6))
        else:
            stdscr.addstr(y, 2, msg, curses.color_pair(6))
        
        stdscr.refresh()
        time.sleep(0.15)
        y += 1
    
    time.sleep(0.5)

def lock_screen(stdscr):
    """Show lock screen"""
    curses.curs_set(0)
    curses.start_color()
    
    # Load configuration
    config = load_config()
    bg_color = get_color_code(config.get('background_color', 'blue'))
    sel_color = get_color_code(config.get('selection_color', 'red'))
    
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_WHITE, sel_color)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, bg_color)
    
    stdscr.bkgd(" ", curses.color_pair(5))
    
    # Get all users
    users = config.get('users', [{'username': 'root', 'password': '', 'home_dir': 'usr/root'}])
    current_user_index = 0
    
    # Find current user index
    current_user_name = config.get('current_user', 'root')
    for i, user in enumerate(users):
        if user['username'] == current_user_name:
            current_user_index = i
            break
    
    while True:
        stdscr.clear()
        
        height, width = stdscr.getmaxyx()
        
        # Get current user info
        current_user = users[current_user_index]
        username = current_user['username']
        password = current_user.get('password', '')
        
        # Display lock screen window
        if not password:
            lines = [
                "",
                "Python-DOS",
                "",
                f"User: {username}",
                "",
                "Press ENTER to login",
                "",
                f"TAB: Switch User ({current_user_index + 1}/{len(users)})",
                "ESC: Shutdown"
            ]
        else:
            lines = [
                "",
                "Python-DOS",
                "",
                f"User: {username}",
                "",
                "Password required",
                "",
                "Press ENTER to login",
                "",
                f"TAB: Switch User ({current_user_index + 1}/{len(users)})",
                "ESC: Shutdown"
            ]
        
        win_height = len(lines) + 4
        win_width = 40
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        draw_window(stdscr, win_y, win_x, win_width, win_height, "Login", lines)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 9:  # TAB - Switch user
            current_user_index = (current_user_index + 1) % len(users)
        
        elif key in [10, 13]:  # ENTER
            if not password:
                # No password - login directly
                config['current_user'] = username
                save_config(config)
                return True
            else:
                # Password required
                entered_password = get_password_input(stdscr, username)
                if entered_password is None:  # ESC pressed
                    continue
                elif entered_password == password:
                    # Correct password - update current user and login
                    config['current_user'] = username
                    save_config(config)
                    return True
                else:
                    # Show error
                    stdscr.clear()
                    error_lines = [
                        "",
                        "Incorrect password!",
                        "",
                        "Press any key to try again"
                    ]
                    draw_window(stdscr, win_y, win_x, win_width, 8, "Error", error_lines)
                    stdscr.refresh()
                    stdscr.getch()
        
        elif key == 27:  # ESC
            return False

def save_config(config):
    """Save configuration to config.json"""
    import json
    try:
        with open('config.json', 'w') as f:
            json.dump(config, indent=4, fp=f)
    except:
        pass

def get_password_input(stdscr, username):
    """Get password input from user"""
    curses.curs_set(1)
    password = ""
    
    height, width = stdscr.getmaxyx()
    
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        # Show password input window
        lines = [
            "",
            f"User: {username}",
            "",
            "Enter Password:",
            "",
            "*" * len(password),
            "",
            "ENTER: Submit | ESC: Cancel"
        ]
        
        win_height = len(lines) + 4
        win_width = 40
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        draw_window(stdscr, win_y, win_x, win_width, win_height, "Password", lines)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            curses.curs_set(0)
            return None
        elif key in [10, 13]:  # ENTER
            curses.curs_set(0)
            return password
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            if password:
                password = password[:-1]
        elif 32 <= key <= 126:
            password += chr(key)

def show_third_party_programs(stdscr):
    """Show and run third party Python programs"""
    import os
    import glob
    
    curses.curs_set(0)
    
    # Get all Python files in third_party_programs folder
    if not os.path.exists('third_party_programs'):
        os.makedirs('third_party_programs')
    
    python_files = glob.glob('third_party_programs/*.py')
    
    if not python_files:
        # No programs found
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        lines = [
            "",
            "No third party programs found!",
            "",
            "Place Python files in:",
            "third_party_programs/",
            "",
            "Press any key to return..."
        ]
        
        height, width = stdscr.getmaxyx()
        win_height = len(lines) + 4
        win_width = 50
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        draw_window(stdscr, win_y, win_x, win_width, win_height, "Third Party Programs", lines)
        stdscr.refresh()
        stdscr.getch()
        return None
    
    # Show list of programs
    program_names = [os.path.basename(f).replace('.py', '') for f in python_files]
    program_names.append("Back")
    selected = 0
    
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(5))
        
        lines = [
            "=== Available Programs ===",
            ""
        ]
        
        for name in program_names:
            lines.append(name)
        
        lines.extend([
            "",
            "UP/DOWN: Navigate | ENTER: Run | ESC: Back"
        ])
        
        height, width = stdscr.getmaxyx()
        win_height = len(lines) + 4
        win_width = 60
        win_y = (height - win_height) // 2
        win_x = (width - win_width) // 2
        
        draw_window(stdscr, win_y, win_x, win_width, win_height, "Third Party Programs", lines, selected + 2)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC
            return None
        elif key == curses.KEY_UP:
            selected = (selected - 1) % len(program_names)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(program_names)
        elif key in [10, 13]:  # ENTER
            choice = program_names[selected]
            
            if choice == "Back":
                return None
            else:
                # Run the selected program
                return python_files[selected]

def get_network_stats(last_stats=None, last_time=None):
    """Get network statistics - returns speed in KB/s"""
    try:
        import psutil
        import time
        
        current_time = time.time()
        net_io = psutil.net_io_counters()
        
        # Get active network interface name - find the one with actual traffic
        active_interface = "Unknown"
        try:
            net_io_per_nic = psutil.net_io_counters(pernic=True)
            max_bytes = 0
            
            for iface, stats in net_io_per_nic.items():
                # Skip loopback interfaces
                if 'loopback' in iface.lower() or 'lo' == iface.lower():
                    continue
                
                # Find interface with most traffic (likely the active one)
                total_bytes = stats.bytes_sent + stats.bytes_recv
                if total_bytes > max_bytes:
                    max_bytes = total_bytes
                    active_interface = iface
            
            # If no interface found, try to get the first non-loopback up interface
            if active_interface == "Unknown":
                net_if_stats = psutil.net_if_stats()
                for iface, stats in net_if_stats.items():
                    if stats.isup and 'loopback' not in iface.lower() and 'lo' != iface.lower():
                        active_interface = iface
                        break
        except:
            active_interface = "Unknown"
        
        if last_stats is None or last_time is None:
            # First call, return 0 speeds
            return {
                'upload': 0,
                'download': 0,
                'connected': True,
                'interface': active_interface,
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'time': current_time
            }
        
        # Calculate time difference
        time_diff = current_time - last_time
        if time_diff == 0:
            time_diff = 0.1
        
        # Calculate speed (bytes per second / 1024 = KB/s)
        upload_speed = (net_io.bytes_sent - last_stats['bytes_sent']) / time_diff / 1024
        download_speed = (net_io.bytes_recv - last_stats['bytes_recv']) / time_diff / 1024
        
        return {
            'upload': max(0, upload_speed),
            'download': max(0, download_speed),
            'connected': True,
            'interface': active_interface,
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'time': current_time
        }
    except:
        return {'upload': 0, 'download': 0, 'connected': False, 'interface': 'N/A', 'bytes_sent': 0, 'bytes_recv': 0, 'time': 0}

def test_network_speed(stdscr):
    """Test network speed by downloading a test file"""
    import urllib.request
    import time
    
    curses.curs_set(0)
    stdscr.nodelay(0)
    stdscr.timeout(-1)
    
    test_lines = [
        "",
        "  Testing network speed...",
        "",
        "  Downloading test file...",
        "",
        "  Please wait...",
        ""
    ]
    
    height, width = stdscr.getmaxyx()
    y = height // 2 - 5
    x = width // 2 - 20
    
    draw_window(stdscr, y, x, 40, 11, "Speed Test", test_lines, use_arrow=False)
    stdscr.refresh()
    
    try:
        # Try multiple test file sources
        test_urls = [
            "http://ipv4.download.thinkbroadband.com/10MB.zip",
            "http://speedtest.tele2.net/10MB.zip",
            "http://proof.ovh.net/files/10Mb.dat"
        ]
        
        success = False
        for test_url in test_urls:
            try:
                # Create request with User-Agent header
                req = urllib.request.Request(
                    test_url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Python-DOS/1.1'}
                )
                
                start_time = time.time()
                response = urllib.request.urlopen(req, timeout=30)
                data = response.read()
                end_time = time.time()
                
                duration = end_time - start_time
                size_mb = len(data) / (1024 * 1024)
                speed_mbps = (size_mb * 8) / duration  # Convert to Mbps
                
                result_lines = [
                    "",
                    f"  Download Speed:",
                    f"  {speed_mbps:.2f} Mbps",
                    "",
                    f"  File Size: {size_mb:.2f} MB",
                    f"  Time: {duration:.2f} seconds",
                    "",
                    "  Press any key to continue",
                    ""
                ]
                
                draw_window(stdscr, y, x, 40, 13, "Speed Test Results", result_lines, use_arrow=False)
                stdscr.refresh()
                stdscr.getch()
                success = True
                break
                
            except:
                continue
        
        if not success:
            raise Exception("All test servers failed")
        
    except Exception as e:
        error_lines = [
            "",
            "  Speed test failed!",
            "",
            "  All test servers",
            "  unavailable or blocked",
            "",
            "  Press any key to continue",
            ""
        ]
        
        draw_window(stdscr, y, x, 40, 12, "Speed Test Error", error_lines, use_arrow=False)
        stdscr.refresh()
        stdscr.getch()
    
    stdscr.nodelay(1)
    stdscr.timeout(100)

def set_system_volume(volume):
    """Set system volume (Windows only)"""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_control = cast(interface, POINTER(IAudioEndpointVolume))
        
        # Set volume (0.0 to 1.0)
        volume_control.SetMasterVolumeLevelScalar(volume / 100.0, None)
        return True
    except:
        return False

def get_system_volume():
    """Get system volume (Windows only)"""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_control = cast(interface, POINTER(IAudioEndpointVolume))
        
        # Get volume (0.0 to 1.0)
        current_volume = volume_control.GetMasterVolumeLevelScalar()
        return int(current_volume * 100)
    except:
        return None

def desktop(stdscr):
    curses.curs_set(0)
    curses.start_color()
    
    # Load configuration
    config = load_config()
    bg_color = get_color_code(config.get('background_color', 'blue'))
    sel_color = get_color_code(config.get('selection_color', 'red'))
    
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)   # window fill
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)   # borders
    curses.init_pair(3, curses.COLOR_WHITE, sel_color)            # selection (configurable)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)   # shadow
    curses.init_pair(5, curses.COLOR_WHITE, bg_color)             # desktop bg (configurable)
    
    stdscr.bkgd(" ", curses.color_pair(5))
    stdscr.nodelay(1)
    stdscr.timeout(100)
    
    # Initialize network stats tracking
    last_net_stats = None
    
    # Initialize terminal instance counter
    terminal_count = 0
    
    # Check for easter egg
    easter_egg_active = (config.get('background_color') == 'green' and 
                        config.get('timezone_offset') == -8)
    
    # Build menu - add Snake Game only if easter egg is active
    menu = ["File Explorer", "Terminal", "Calculator", "Notepad", "Python IDE", 
            "Music Player", "Web Browser", "Settings", "App Maker", "App Store", 
            "Third Party Programs", "Network Speed Test"]
    
    if easter_egg_active:
        menu.append("Snake Game")
    
    menu.extend(["Log Out", "Restart", "Bootloader", "Shutdown"])
    
    selected = 0
    
    while True:
        import datetime
        stdscr.clear()
        
        height, width = stdscr.getmaxyx()
        
        # Get current time
        tz_offset = config.get('timezone_offset', 0)
        current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=tz_offset)
        time_str = current_time.strftime("%H:%M:%S")
        date_str = current_time.strftime("%Y-%m-%d")
        hour = current_time.hour
        minute = current_time.minute
        second = current_time.second
        
        # Calculate responsive positions based on window size
        menu_width = 35
        menu_height = len(menu) + 4
        menu_x = 5
        menu_y = 5
        
        volume_width = 38
        volume_height = 12
        volume_x = menu_x + menu_width + 5  # 5 spaces after menu
        volume_y = 5
        
        clock_width = 28
        clock_height = 9
        clock_x = volume_x + volume_width + 5  # 5 spaces after volume
        clock_y = 5
        
        net_width = 38
        net_height = 10
        net_x = volume_x
        net_y = volume_y + volume_height + 1  # 1 space below volume
        
        # Draw main menu with > selection (left side)
        draw_window(stdscr, menu_y, menu_x, menu_width, menu_height, "Main Menu", menu, selected, use_arrow=True)
        
        # Draw Volume Control widget
        # Try to get system volume, fallback to config
        system_volume = get_system_volume()
        if system_volume is not None:
            volume = system_volume
            config['volume'] = volume  # Sync config with system
        else:
            volume = config.get('volume', 50)
        
        volume_lines = [
            "",
            f"  Volume: {volume}%",
            "",
            "  " + "█" * (volume // 5) + "░" * (20 - volume // 5),
            "",
            "  Press + to increase",
            "  Press - to decrease",
            ""
        ]
        draw_window(stdscr, volume_y, volume_x, volume_width, volume_height, "Volume Control", volume_lines, use_arrow=False)
        
        # Draw Clock widget
        clock_lines = [
            "",
            f"  {time_str}",
            "",
            f"  {date_str}",
            ""
        ]
        draw_window(stdscr, clock_y, clock_x, clock_width, clock_height, "Clock", clock_lines, use_arrow=False)
        
        # Draw Network Monitor widget
        # Get network stats (pass previous stats for speed calculation)
        if last_net_stats is None:
            net_stats = get_network_stats()
        else:
            net_stats = get_network_stats(last_net_stats, last_net_stats.get('time'))
        last_net_stats = net_stats
        
        if net_stats['connected']:
            status = "Connected"
            interface = net_stats.get('interface', 'Unknown')
            upload_str = f"  Upload:   {net_stats['upload']:>8.2f} KB/s"
            download_str = f"  Download: {net_stats['download']:>8.2f} KB/s"
        else:
            status = "Disconnected"
            interface = "N/A"
            upload_str = "  Upload:   N/A"
            download_str = "  Download: N/A"
        
        net_lines = [
            "",
            f"  Interface: {interface[:20]}",
            f"  Status: {status}",
            "",
            upload_str,
            download_str,
            ""
        ]
        draw_window(stdscr, net_y, net_x, net_width, 11, "Network Monitor", net_lines, use_arrow=False)
        draw_window(stdscr, net_y, net_x, net_width, net_height, "Network Monitor", net_lines, use_arrow=False)
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == -1:  # No key pressed (timeout)
            continue
        
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(menu)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(menu)
        elif key == ord('+') or key == ord('='):  # + key (with or without shift)
            # Increase volume
            import json
            volume = config.get('volume', 50)
            volume = min(100, volume + 5)
            
            # Try to set system volume
            if not set_system_volume(volume):
                # Fallback to config only
                config['volume'] = volume
                try:
                    with open('config.json', 'w') as f:
                        json.dump(config, f, indent=4)
                except:
                    pass
        elif key == ord('-') or key == ord('_'):  # - key (with or without shift)
            # Decrease volume
            import json
            volume = config.get('volume', 50)
            volume = max(0, volume - 5)
            
            # Try to set system volume
            if not set_system_volume(volume):
                # Fallback to config only
                config['volume'] = volume
                try:
                    with open('config.json', 'w') as f:
                        json.dump(config, f, indent=4)
                except:
                    pass
        elif key in [10, 13]:
            stdscr.nodelay(0)
            stdscr.timeout(-1)
            choice = menu[selected]
            
            if choice == "File Explorer":
                curses.endwin()
                subprocess.run(["python", "apps/file_explorer.py"])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
                stdscr.nodelay(1)
                stdscr.timeout(100)
            
            elif choice == "Terminal":
                terminal_count += 1
                curses.endwin()
                subprocess.run(["python", "apps/terminal.py", str(terminal_count)])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
                stdscr.nodelay(1)
                stdscr.timeout(100)
            
            elif choice == "Calculator":
                curses.endwin()
                subprocess.run(["python", "apps/calculator.py"])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
            
            elif choice == "Notepad":
                curses.endwin()
                subprocess.run(["python", "apps/notepad.py"])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
            
            elif choice == "Python IDE":
                curses.endwin()
                subprocess.run(["python", "apps/python_ide.py"])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
            
            elif choice == "Music Player":
                curses.endwin()
                subprocess.run(["python", "apps/music_player.py"])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
            
            elif choice == "Web Browser":
                curses.endwin()
                subprocess.run(["python", "apps/web_browser.py"])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
            
            elif choice == "Settings":
                curses.endwin()
                subprocess.run(["python", "apps/settings.py"])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
            
            elif choice == "App Maker":
                curses.endwin()
                subprocess.run(["python", "apps/app_maker.py"])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
            
            elif choice == "App Store":
                curses.endwin()
                subprocess.run(["python", "apps/app_store.py"])
                # Reinitialize curses after app exits
                stdscr = curses.initscr()
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.keypad(True)
            
            elif choice == "Third Party Programs":
                program_path = show_third_party_programs(stdscr)
                if program_path:
                    # Run the selected third party program
                    curses.endwin()
                    subprocess.run(["python", program_path])
                    # Reinitialize curses after program exits
                    stdscr = curses.initscr()
                    curses.start_color()
                    config = load_config()
                    bg_color = get_color_code(config.get('background_color', 'blue'))
                    sel_color = get_color_code(config.get('selection_color', 'red'))
                    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                    curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                    curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                    stdscr.bkgd(" ", curses.color_pair(5))
                    curses.curs_set(0)
                    stdscr.keypad(True)
                    stdscr.nodelay(1)
                    stdscr.timeout(100)
            
            elif choice == "Network Speed Test":
                test_network_speed(stdscr)
                # Reinitialize after test
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
                stdscr.nodelay(1)
                stdscr.timeout(100)
            
            elif choice == "Snake Game":
                # Easter egg unlocked! Show special message
                stdscr.clear()
                stdscr.bkgd(" ", curses.color_pair(5))
                
                easter_lines = [
                    "",
                    "*** EASTER EGG UNLOCKED! ***",
                    "",
                    "You discovered the secret!",
                    "",
                    "Green background + PST timezone",
                    "= Hidden Snake Game",
                    "",
                    "Press any key to play..."
                ]
                
                height, width = stdscr.getmaxyx()
                win_height = len(easter_lines) + 4
                win_width = 50
                win_y = (height - win_height) // 2
                win_x = (width - win_width) // 2
                
                draw_window(stdscr, win_y, win_x, win_width, win_height, "Easter Egg", easter_lines)
                stdscr.refresh()
                stdscr.getch()
                
                snake_game(stdscr)
                
                # Reinitialize colors after game
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                curses.curs_set(0)
            
            elif choice == "Log Out":
                stdscr.clear()
                stdscr.bkgd(" ", curses.color_pair(5))
                draw_window(stdscr, 5, 10, 35, 5, "Logging Out", ["Logging out..."])
                stdscr.refresh()
                import time
                time.sleep(1)
                return "logout"
            
            elif choice == "Restart":
                stdscr.clear()
                stdscr.bkgd(" ", curses.color_pair(5))
                draw_window(stdscr, 5, 10, 35, 5, "Restarting", ["System restarting..."])
                stdscr.refresh()
                import time
                time.sleep(1)
                # Show boot sequence
                boot_sequence(stdscr)
                # Reinitialize colors for desktop
                curses.start_color()
                config = load_config()
                bg_color = get_color_code(config.get('background_color', 'blue'))
                sel_color = get_color_code(config.get('selection_color', 'red'))
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
                curses.init_pair(3, curses.COLOR_WHITE, sel_color)
                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_WHITE, bg_color)
                stdscr.bkgd(" ", curses.color_pair(5))
                # Reset selection
                selected = 0
            
            elif choice == "Bootloader":
                stdscr.clear()
                stdscr.bkgd(" ", curses.color_pair(5))
                draw_window(stdscr, 5, 10, 35, 5, "Rebooting", ["Returning to bootloader..."])
                stdscr.refresh()
                import time
                time.sleep(1)
                # Exit to bootloader
                curses.endwin()
                subprocess.run(["python", "bootloader/bootloader.py"])
                # When bootloader exits, we're done
                return "bootloader"
            
            elif choice == "Shutdown":
                stdscr.clear()
                draw_window(stdscr, 5, 10, 35, 5, "Shutdown", ["System shutting down..."])
                stdscr.refresh()
                stdscr.getch()
                break

def snake_game(stdscr):
    """Easter egg: Snake game"""
    import random
    import time
    
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)
    
    height, width = stdscr.getmaxyx()
    
    # Game window size - make it larger
    game_width = min(70, width - 10)
    game_height = min(30, height - 8)
    game_y = (height - game_height) // 2
    game_x = (width - game_width) // 2
    
    # Draw game window with shadow
    for i in range(game_height):
        stdscr.addstr(game_y + i, game_x, " " * game_width, curses.color_pair(1))
    
    # Draw borders
    stdscr.attron(curses.color_pair(2))
    stdscr.addstr(game_y, game_x, "┌" + "─" * (game_width - 2) + "┐")
    for i in range(1, game_height - 1):
        stdscr.addstr(game_y + i, game_x, "│" + " " * (game_width - 2) + "│")
    stdscr.addstr(game_y + game_height - 1, game_x, "└" + "─" * (game_width - 2) + "┘")
    stdscr.attroff(curses.color_pair(2))
    
    # Draw title
    title = " Snake Game "
    stdscr.addstr(game_y, game_x + 2, title, curses.color_pair(1))
    
    # Draw shadow
    stdscr.attron(curses.color_pair(4))
    for i in range(game_height):
        stdscr.addstr(game_y + i, game_x + game_width, "  ")
    stdscr.addstr(game_y + game_height, game_x + 2, " " * game_width)
    stdscr.attroff(curses.color_pair(4))
    
    # Play area inside window
    play_width = game_width - 4
    play_height = game_height - 4
    play_y = game_y + 2
    play_x = game_x + 2
    
    # Snake starting position
    snake = [[play_height // 2, play_width // 2]]
    direction = curses.KEY_RIGHT
    
    # Food position
    food = [random.randint(0, play_height - 1), random.randint(0, play_width - 1)]
    
    score = 0
    
    while True:
        # Clear play area
        for i in range(play_height):
            stdscr.addstr(play_y + i, play_x, " " * play_width, curses.color_pair(1))
        
        # Draw score at bottom of window
        score_text = f"Score: {score} | Arrow Keys: Move | ESC: Exit"
        stdscr.addstr(game_y + game_height - 1, game_x + 2, " " * (game_width - 4), curses.color_pair(1))
        stdscr.addstr(game_y + game_height - 1, game_x + (game_width - len(score_text)) // 2, score_text, curses.color_pair(1))
        
        # Draw food
        if 0 <= food[0] < play_height and 0 <= food[1] < play_width:
            stdscr.addstr(play_y + food[0], play_x + food[1], "O", curses.color_pair(3))
        
        # Draw snake
        for segment in snake:
            if 0 <= segment[0] < play_height and 0 <= segment[1] < play_width:
                stdscr.addstr(play_y + segment[0], play_x + segment[1], "■", curses.color_pair(2))
        
        stdscr.refresh()
        
        # Get key
        key = stdscr.getch()
        
        if key == 27:  # ESC
            break
        
        # Change direction
        if key == curses.KEY_UP and direction != curses.KEY_DOWN:
            direction = curses.KEY_UP
        elif key == curses.KEY_DOWN and direction != curses.KEY_UP:
            direction = curses.KEY_DOWN
        elif key == curses.KEY_LEFT and direction != curses.KEY_RIGHT:
            direction = curses.KEY_LEFT
        elif key == curses.KEY_RIGHT and direction != curses.KEY_LEFT:
            direction = curses.KEY_RIGHT
        
        # Move snake
        head = snake[0].copy()
        
        if direction == curses.KEY_UP:
            head[0] -= 1
        elif direction == curses.KEY_DOWN:
            head[0] += 1
        elif direction == curses.KEY_LEFT:
            head[1] -= 1
        elif direction == curses.KEY_RIGHT:
            head[1] += 1
        
        # Check collision with walls
        if head[0] < 0 or head[0] >= play_height or head[1] < 0 or head[1] >= play_width:
            # Game over
            game_over_lines = [
                "",
                "GAME OVER!",
                "",
                f"Final Score: {score}",
                "",
                "Press any key to exit..."
            ]
            go_height = len(game_over_lines) + 4
            go_width = 40
            go_y = (height - go_height) // 2
            go_x = (width - go_width) // 2
            
            draw_window(stdscr, go_y, go_x, go_width, go_height, "Game Over", game_over_lines)
            stdscr.nodelay(0)
            stdscr.refresh()
            stdscr.getch()
            break
        
        # Check collision with self
        if head in snake:
            # Game over
            game_over_lines = [
                "",
                "GAME OVER!",
                "",
                f"Final Score: {score}",
                "",
                "Press any key to exit..."
            ]
            go_height = len(game_over_lines) + 4
            go_width = 40
            go_y = (height - go_height) // 2
            go_x = (width - go_width) // 2
            
            draw_window(stdscr, go_y, go_x, go_width, go_height, "Game Over", game_over_lines)
            stdscr.nodelay(0)
            stdscr.refresh()
            stdscr.getch()
            break
        
        snake.insert(0, head)
        
        # Check if food eaten
        if head == food:
            score += 10
            # Generate new food
            while True:
                food = [random.randint(0, play_height - 1), random.randint(0, play_width - 1)]
                if food not in snake:
                    break
        else:
            snake.pop()
    
    stdscr.nodelay(0)
    stdscr.timeout(-1)

def main(stdscr):
    # Create boot log
    create_boot_log()
    
    # Validate user folders before boot
    validate_user_folders()
    
    # Show boot sequence only once at startup
    boot_sequence(stdscr)
    
    while True:
        # Show lock screen
        if not lock_screen(stdscr):
            # User pressed ESC on lock screen - shutdown
            break
        
        # User logged in - show desktop
        result = desktop(stdscr)
        
        # If desktop returns "logout", go back to lock screen (no reboot)
        # If desktop returns "bootloader", exit to bootloader
        # If desktop returns None or anything else, exit completely
        if result == "logout":
            continue  # Go back to lock screen
        elif result == "bootloader":
            break  # Exit to bootloader
        else:
            break  # Shutdown

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Failed to start: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
