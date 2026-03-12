# Changelog

All notable changes to Python-DOS will be documented in this file.

## [1.1.0] - 2026-03-12

### Added
- **Desktop Widgets System**
  - Volume Control widget with visual bar and +/- controls
  - Network Monitor widget showing interface name, status, and real-time speeds
  - Clock widget displaying time and date
  - All widgets positioned responsively based on window size
  
- **Network Speed Test**
  - New menu option to test download speed
  - Downloads 10MB test file and displays speed in Mbps
  - Shows file size and time taken
  
- **Native System Integration**
  - Volume control now adjusts Windows system volume (requires pycaw)
  - Network monitor shows actual network interface name (requires psutil)
  - Real-time upload/download speed monitoring in KB/s
  
- **App Store**
  - Download community apps from GitHub repository
  - Browse available apps with descriptions
  - Shows [INSTALLED] status for downloaded apps
  - Automatic installation to third_party_programs folder
  - Scrollbar support for long app lists
  
- **App Maker IDE**
  - Three-panel layout: Editor, Preview, Terminal
  - Line numbers in editor
  - F2 to save, F5 to run/preview, F6 to edit in Notepad
  - Real-time error display in terminal panel
  - Create new apps or edit existing ones
  
- **Third Party Programs Menu**
  - Automatically scans third_party_programs folder
  - Lists all .py files for execution
  - Shows "No programs found" when folder is empty
  - Includes README with instructions
  
- **Boot Cache System**
  - Logs boot time, Python version, platform info
  - Records configuration settings and user info
  - Tracks system file sizes
  - Timestamped log files in boot_cache folder
  
- **Terminal Enhancements**
  - Python REPL mode (type 'python' to enter)
  - Interactive Python interpreter with >>> prompt
  - Variables persist across commands
  - ESC to exit Python mode
  - Multiple terminal instances with unique numbers
  
- **Snake Game Easter Egg**
  - Hidden game unlocked with green background + PST timezone
  - Only appears in menu when conditions are met
  - Special unlock message when discovered
  
- **Example Apps**
  - Paint app with save functionality (saves to Documents)
  - Color picker with RGB values
  - Todo list manager
  - Stopwatch with lap times
  - Multiple sample apps for learning

### Changed
- Settings now use timezone offsets instead of regions (10 common timezones)
- Menu selection now uses `>` symbol instead of just highlighting
- Desktop runs in real-time mode with nodelay for live widget updates
- All apps properly reinitialize curses after exit to prevent crashes
- Terminal type set to xterm-256color for simulated terminal support
- Widget positioning calculated dynamically for perfect alignment

### Fixed
- Apps no longer exit to command line after logout
- Properly restore curses state after app exits
- Settings region tab no longer returns to main menu
- App Maker no longer crashes when creating/editing apps
- Network monitor updates without blocking UI
- Removed duplicate widget rendering code

### Technical
- Added support for simulated terminals (Windows Terminal, VSCode, etc.)
- Improved curses initialization and cleanup
- Better error handling for missing dependencies
- Modular widget positioning system
- Network stats tracked between frames for accurate speed calculation

## [1.0.0] - Initial Release

### Added
- Main desktop with menu system
- File Explorer with directory navigation
- Terminal with command execution
- Calculator with basic operations
- Notepad text editor with save/load
- Python IDE with syntax highlighting
- Music Player with MP3/WAV/OGG support
- Web Browser (text-only)
- Settings with customizable colors and scaling
- Bootloader with boot sequence animation
- Lock screen with user authentication
- Shutdown/Restart/Bootloader options
- Classic blue GUI with shadows
- Arrow key navigation
- ESC to exit apps

### Features
- Multi-user support
- Configuration persistence (config.json)
- User home directories
- Safe mode and single user mode
- Verbose mode for debugging
- Windows-style interface
- Shadow effects on all windows

---

## Installation

```bash
pip install windows-curses pygame psutil pycaw
```

## Optional Dependencies

- **pygame**: Required for Music Player
- **psutil**: Required for Network Monitor
- **pycaw**: Required for native Windows volume control

Without optional dependencies, the system will still run but with reduced functionality.
