@echo off
cls
echo EZI will use XCOPY.EXE to copy AGE OF EMPIRES to C:\EMPIRE
echo Press any key to continue
pause >nul
md c:\EMPIRE
xcopy \EMPIRE c:\EMPIRE /e 
c:
cd\EMPIRE
echo Installation Successful.
echo.
echo 1. Change directory to C:\EMPIRE
echo 2. Run SETUP.EXE to configure resgistry
echo 3. Run EMPIRES.EXE to play!