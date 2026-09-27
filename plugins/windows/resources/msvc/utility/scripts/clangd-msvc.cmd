@echo off
rem clangd launcher that supplies the MSVC developer environment. clangd's own Visual Studio
rem discovery selects the newest Setup instance even when it has no C++ tools, then cannot
rem find windows.h or the MSVC STL. Install with Install-ClangdMsvc.ps1; stdout carries LSP,
rem so only clangd may write to it.
setlocal
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if exist "%VSWHERE%" for /f "usebackq delims=" %%i in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VS_INSTALL=%%i"
if defined VS_INSTALL call "%VS_INSTALL%\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
if not defined CLANGD_EXECUTABLE set "CLANGD_EXECUTABLE=clangd"
"%CLANGD_EXECUTABLE%" %*
