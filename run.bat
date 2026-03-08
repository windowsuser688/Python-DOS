@echo off
echo Setting console font to Raster 8x12...
reg add "HKCU\Console" /v FaceName /t REG_SZ /d "Terminal" /f >nul 2>&1
reg add "HKCU\Console" /v FontFamily /t REG_DWORD /d 54 /f >nul 2>&1
reg add "HKCU\Console" /v FontSize /t REG_DWORD /d 0x000c0008 /f >nul 2>&1
reg add "HKCU\Console" /v FontWeight /t REG_DWORD /d 400 /f >nul 2>&1

echo Installing required library...
pip install windows-curses >nul 2>&1
echo.
echo Starting Python-DOS Bootloader...
python bootloader/bootloader.py
echo.
echo Program ended. Press any key to close...
pause > nul
