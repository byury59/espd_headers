@echo off
rem Перед первой сборкой один раз установите библиотеки:
rem     python -m pip install chardet pyinstaller
rem chardet - для работы программы (необязательна), PyInstaller - для сборки exe.
rem Полный список - в Инструкция.txt, раздел 9.
rem Если PyInstaller не установлен, build.py сообщит об этом и сборка остановится.

rem Лежит в папке scripts, работает из корня репозитория
cd /d "%~dp0.."

echo === Building espd_headers ===
python build.py
if errorlevel 1 goto error

echo.
echo Build finished: see dist\espd_headers_^<version^>
pause
exit /b 0

:error
echo.
echo BUILD FAILED
pause
exit /b 1
