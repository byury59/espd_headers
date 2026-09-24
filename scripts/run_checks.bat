@echo off
rem ---------------------------------------------------------------------------
rem  Automatic checks of espd_headers. No questions asked - just run it.
rem  Программа меняет файлы на месте, поэтому каждый прогон идёт на копии
rem  TestProject в папке checks. Каждая копия обрабатывается дважды: второй
rem  прогон не должен ничего менять (защита от дублей шапок).
rem  Progress is shown here, full output goes to checks\checks_log.txt.
rem ---------------------------------------------------------------------------
setlocal EnableDelayedExpansion
rem UTF-8 for the whole log, including cmd tools like "where"
chcp 65001 >nul
cd /d "%~dp0.."
set "ROOT=%CD%"
set "PYTHONIOENCODING=utf-8"
set "OUT=%ROOT%\checks"
if exist "%OUT%" rmdir /s /q "%OUT%"
mkdir "%OUT%"
set "LOG=%OUT%\checks_log.txt"
set "N=0"

>"%LOG%" echo === run_checks %date% %time% ===
call :header "Environment"
where python >>"%LOG%" 2>&1
python --version >>"%LOG%" 2>&1 <nul
python -c "import chardet; print('chardet OK')" >>"%LOG%" 2>&1 <nul
python -u src\main.py --version >>"%LOG%" 2>&1 <nul

set "CMD=python -u "%ROOT%\src\main.py""
call :run_set source

call :header "ERROR CASE path does not exist, expect exit code 1"
python -u src\main.py --path TestProject\no_such_folder --out "%OUT%\source\results" --yes >>"%LOG%" 2>&1 <nul
>>"%LOG%" echo exit code: %errorlevel%

call :header "CANCEL answer n, expect no changes and exit code 0"
xcopy "%ROOT%\TestProject" "%OUT%\cancel\TestProject\" /e /i /q >nul
echo n| python -u src\main.py --path "%OUT%\cancel\TestProject" --out "%OUT%\cancel\results" >>"%LOG%" 2>&1
>>"%LOG%" echo exit code: %errorlevel%
call :compare "%ROOT%\TestProject" "%OUT%\cancel\TestProject"

set "EXE="
for /d %%d in (dist\espd_headers_*) do set "EXE=%ROOT%\%%d\%%~nxd.exe"
if not defined EXE goto no_exe
if not exist "%EXE%" goto no_exe

call :header "EXE version"
"%EXE%" --version >>"%LOG%" 2>&1 <nul
set "CMD="%EXE%""
call :run_set exe
goto finish

:no_exe
call :header "EXE not built yet, skipped"

:finish
>>"%LOG%" echo.
>>"%LOG%" echo === finished %date% %time% ===
echo.
echo Done. Results: %LOG%
pause
exit /b 0

rem ---------------------------------------------------------------------------
:run_set
rem %1 - имя набора (source или exe). Копия TestProject, два прогона, сравнение.
set "W=%OUT%\%~1"
xcopy "%ROOT%\TestProject" "%W%\TestProject\" /e /i /q >nul
call :header "%~1: first run"
!CMD! --path "%W%\TestProject" --out "%W%\results" --yes >>"%LOG%" 2>&1 <nul
>>"%LOG%" echo exit code: !errorlevel!
xcopy "%W%\TestProject" "%W%\after_run1\" /e /i /q >nul
call :header "%~1: second run, expect no changes"
!CMD! --path "%W%\TestProject" --out "%W%\results" --yes >>"%LOG%" 2>&1 <nul
>>"%LOG%" echo exit code: !errorlevel!
call :compare "%W%\after_run1" "%W%\TestProject"
exit /b 0

rem ---------------------------------------------------------------------------
:compare
rem Сравнивает две папки побайтно, в лог - список различающихся файлов.
python -c "import sys,os,filecmp; a,b=sys.argv[1],sys.argv[2]; bad=[os.path.relpath(os.path.join(r,f),a) for r,_,fs in os.walk(a) for f in fs if not filecmp.cmp(os.path.join(r,f),os.path.join(b,os.path.relpath(os.path.join(r,f),a)),shallow=False)]; print('changed files:', bad if bad else 'none')" "%~1" "%~2" >>"%LOG%" 2>&1 <nul
exit /b 0

rem ---------------------------------------------------------------------------
:header
set /a N+=1
echo [!N!] %~1
>>"%LOG%" echo.
>>"%LOG%" echo ===== [!N!] %~1 =====
exit /b 0
