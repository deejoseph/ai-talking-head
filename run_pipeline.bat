@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

cd /d %~dp0

set "ENV_NAME=pixel_ai"
set "CONDA_BAT="
set "PROJECT_DIR=%CD%"

rem Keep runtime/cache files on project disk (D:) to avoid C: growth
set "LOCAL_TMP=%PROJECT_DIR%\.tmp"
set "LOCAL_CACHE=%PROJECT_DIR%\.cache"
if not exist "%LOCAL_TMP%" mkdir "%LOCAL_TMP%"
if not exist "%LOCAL_CACHE%" mkdir "%LOCAL_CACHE%"
if not exist "%LOCAL_CACHE%\torch" mkdir "%LOCAL_CACHE%\torch"
if not exist "%LOCAL_CACHE%\huggingface" mkdir "%LOCAL_CACHE%\huggingface"
if not exist "%LOCAL_CACHE%\pip" mkdir "%LOCAL_CACHE%\pip"
if not exist "%LOCAL_CACHE%\matplotlib" mkdir "%LOCAL_CACHE%\matplotlib"

set "TEMP=%LOCAL_TMP%"
set "TMP=%LOCAL_TMP%"
set "TORCH_HOME=%LOCAL_CACHE%\torch"
set "HF_HOME=%LOCAL_CACHE%\huggingface"
set "PIP_CACHE_DIR=%LOCAL_CACHE%\pip"
set "MPLCONFIGDIR=%LOCAL_CACHE%\matplotlib"

where conda >nul 2>nul
if %ERRORLEVEL%==0 (
    call conda activate %ENV_NAME%
) else (
    if exist "%USERPROFILE%\anaconda3\condabin\conda.bat" set "CONDA_BAT=%USERPROFILE%\anaconda3\condabin\conda.bat"
    if exist "%USERPROFILE%\miniconda3\condabin\conda.bat" set "CONDA_BAT=%USERPROFILE%\miniconda3\condabin\conda.bat"
    if defined CONDA_BAT (
        call "%CONDA_BAT%" activate %ENV_NAME%
    ) else (
        echo [ERROR] Conda not found. Please install/initialize Conda first.
        pause
        exit /b 1
    )
)

if not %ERRORLEVEL%==0 (
    echo [ERROR] Failed to activate conda env: %ENV_NAME%
    pause
    exit /b 1
)

echo ===============================
echo UI Params:
echo PADS=%PADS%
echo RESIZE=%RESIZE%
echo FACE_BS=%FACE_BS%
echo WAV_BS=%WAV_BS%
echo POSE_STYLE=%POSE_STYLE%
echo EXPRESSION_SCALE=%EXPRESSION_SCALE%
echo FIX_HEAD=%FIX_HEAD%
echo PREPROCESS=%PREPROCESS%
echo SMOOTH_FACE=%SMOOTH_FACE%
echo ===============================

echo [INFO] Launching Gradio UI: http://127.0.0.1:7860
python app.py
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
    echo [ERROR] app.py failed with exit code %EXIT_CODE%.
    pause
    exit /b %EXIT_CODE%
)

echo [OK] Gradio app exited.
pause
