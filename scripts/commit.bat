@echo off
rem ---------------------------------------------------------------------------
rem  Universal commit helper.
rem
rem  Put this file anywhere inside a git project (root or a scripts folder) and run it.
rem  You type two things: the branch (Enter = stay on the current one)
rem  and the commit message. Everything else - add, commit, push - is automatic.
rem
rem  The version shown in the header is picked up from package.json,
rem  pyproject.toml, Cargo.toml, VERSION or src\...\__init__.py, if present.
rem ---------------------------------------------------------------------------
setlocal EnableDelayedExpansion
cd /d "%~dp0"

where git >nul 2>nul || (echo Git not found. & pause & exit /b 1)

git rev-parse --is-inside-work-tree >nul 2>nul || (
    echo This folder is not a git repository: %cd%
    echo Run  git init  first, or move this file into a project.
    pause
    exit /b 1
)

git remote get-url origin >nul 2>nul || (
    echo No remote named 'origin'. Add it first:
    echo     git remote add origin https://github.com/USER/REPO.git
    pause
    exit /b 1
)

rem --- Project name = name of the repository root folder ---
set "ROOT="
for /f "delims=" %%r in ('git rev-parse --show-toplevel') do set "ROOT=%%r"
set "ROOT=!ROOT:/=\!"
for %%r in ("!ROOT!") do set "PROJECT=%%~nxr"
rem Work from the repository root, wherever this file lies.
cd /d "!ROOT!"

call :detect_version
call :read_branch_state

if defined VER (
    echo === !PROJECT!   branch: !BRANCH!   version: !VER! ===
) else (
    echo === !PROJECT!   branch: !BRANCH! ===
)
echo.
echo === Changes ===
git status --short
echo.

rem --- 1. Branch ---
set "TARGET="
set /p "TARGET=Branch (Enter = !BRANCH!): "
if defined TARGET if /i not "!TARGET!"=="!BRANCH!" (
    git show-ref --verify --quiet "refs/heads/!TARGET!"
    if errorlevel 1 (
        echo Creating branch !TARGET!
        git switch -c "!TARGET!" || goto error
    ) else (
        git switch "!TARGET!" || goto error
    )
    call :read_branch_state
)

rem --- 2. Message ---
git status --porcelain | findstr . >nul || goto push_only

if defined VER echo Example message: !VER!: what was changed
echo Do not use double quotes in the message.
set "MSG="
set /p "MSG=Changes (empty = cancel): "
if not defined MSG (echo Cancelled. & pause & exit /b 0)

git add -A || goto error
git commit -m "!MSG!" || goto error
call :push || goto error
goto done

:push_only
rem Nothing to commit - maybe there are commits that never reached GitHub.
if not defined HASUP (
    echo Nothing to commit, but branch !BRANCH! is not on GitHub yet.
    set "ANS="
    set /p "ANS=Push it now? y/n: "
    if /i not "!ANS!"=="y" (echo Cancelled. & pause & exit /b 0)
    call :push || goto error
    goto done
)

set "AHEAD=0"
for /f %%n in ('git rev-list --count @{u}..HEAD 2^>nul') do set "AHEAD=%%n"
if "!AHEAD!"=="0" (
    echo Nothing to commit. Everything is already on GitHub.
    pause
    exit /b 0
)
echo Nothing to commit, but !AHEAD! commit[s] are not on GitHub yet:
git log --oneline @{u}..HEAD
set "ANS="
set /p "ANS=Push them now? y/n: "
if /i not "!ANS!"=="y" (echo Cancelled. & pause & exit /b 0)
call :push || goto error

:done
echo.
echo Done: !BRANCH! is on GitHub.
pause
exit /b 0

rem ---------------------------------------------------------------------------
:read_branch_state
rem Current branch name and whether it is linked to a branch on GitHub.
set "BRANCH="
for /f %%b in ('git rev-parse --abbrev-ref HEAD') do set "BRANCH=%%b"
set "HASUP="
git rev-parse --abbrev-ref --symbolic-full-name @{u} >nul 2>nul && set "HASUP=1"
exit /b 0

rem ---------------------------------------------------------------------------
:push
rem The first push of a new branch needs -u to link it to origin.
if defined HASUP (
    git push
) else (
    git push -u origin "!BRANCH!"
)
exit /b !errorlevel!

rem ---------------------------------------------------------------------------
:detect_version
rem Sets VER if the project declares a version somewhere known. Silent if not.
set "VER="
set "RAW="

if exist "package.json" (
    for /f "tokens=2 delims=:," %%v in ('findstr /c:"\"version\":" package.json') do if not defined RAW set "RAW=%%v"
    call :clean_raw
    if defined VER exit /b 0
)

if exist "pyproject.toml" (
    for /f "tokens=2 delims==" %%v in ('findstr /r /c:"^version *=" pyproject.toml') do if not defined RAW set "RAW=%%v"
    call :clean_raw
    if defined VER exit /b 0
)

if exist "Cargo.toml" (
    for /f "tokens=2 delims==" %%v in ('findstr /r /c:"^version *=" Cargo.toml') do if not defined RAW set "RAW=%%v"
    call :clean_raw
    if defined VER exit /b 0
)

if exist "VERSION" (
    for /f "delims=" %%v in (VERSION) do if not defined RAW set "RAW=%%v"
    call :clean_raw
    if defined VER exit /b 0
)

rem Python packages keep __version__ inside src\<package>\__init__.py
if exist "src" (
    for /f "tokens=2 delims='" %%v in ('findstr /s /c:"__version__" "src\*.py" 2^>nul') do if not defined RAW set "RAW=%%v"
    call :clean_raw
)
exit /b 0

rem ---------------------------------------------------------------------------
:clean_raw
rem Strips quotes, spaces and trailing comma from a version found in a file.
if not defined RAW exit /b 0
set "RAW=!RAW: =!"
set "RAW=!RAW:"=!"
set "RAW=!RAW:'=!"
set "RAW=!RAW:,=!"
if defined RAW set "VER=!RAW!"
set "RAW="
exit /b 0

rem ---------------------------------------------------------------------------
:error
echo.
echo FAILED - see messages above.
pause
exit /b 1
