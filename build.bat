@echo off
setlocal EnableDelayedExpansion

:: 1. CONTROLE DE VERSÃO
set VERSION_FILE=version.txt
if not exist %VERSION_FILE% echo 0.0.0> %VERSION_FILE%

for /f "tokens=1,2,3 delims=." %%a in (%VERSION_FILE%) do (
    set MAJOR=%%a
    set MINOR=%%b
    set PATCH=%%c
)
set /a PATCH+=1
set NEW_VERSION=%MAJOR%.%MINOR%.!PATCH!
echo !NEW_VERSION!> %VERSION_FILE%

echo ==========================================
echo 👻 INICIANDO BUILD DO COOKIEJAR v!NEW_VERSION!
echo ==========================================

:: 2. LIMPEZA DE BUILDS ANTIGOS
echo Limpando pastas temporarias...
rmdir /s /q build dist >nul 2>&1

:: 3. COMPILACAO PYINSTALLER
:: Verifica se o pyinstaller esta instalado
pip install pyinstaller Pillow customtkinter >nul 2>&1 

echo Construindo o Executavel...
pyinstaller ^
--noconsole ^
--onefile ^
--windowed ^
--icon=app-icon.ico ^
--add-data "app-logo.png;." ^
--add-data "app-icon.ico;." ^
--add-data "version.txt;." ^
--name "CookieJar" main.py

:: 4. COMPILACAO DO INSTALADOR (INNO SETUP)
echo Criando o Instalador...
:: Altere o caminho abaixo se o seu Inno Setup estiver instalado em outro local!
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /DMyAppVersion="!NEW_VERSION!" installer.iss

echo ==========================================
echo ✅ BUILD E INSTALADOR GERADOS COM SUCESSO!
echo ==========================================
pause