@echo off
REM Inicio Rápido - Proyecto de Arquitectura de Juego (Windows)

cls
echo.
echo ========================================================
echo Taller 62 - Arquitectura de Juego, Escenas y Navegacion
echo ========================================================
echo.
echo Ubicacion actual: %cd%
echo.

REM Check if node_modules exists
if exist "node_modules\" (
    echo [OK] Dependencias ya estan instaladas
) else (
    echo [*] Instalando dependencias...
    call npm install
)

echo.
echo [*] Iniciando servidor de desarrollo...
echo.
echo La aplicacion estara disponible en: http://localhost:5173
echo.
echo Escenas disponibles:
echo   + Menu Principal      %  /
echo   + Juego Interactivo   %  /juego
echo   + Creditos del Proyecto %  /creditos
echo.
echo Tips:
echo   - Use el raton para rotar y hacer zoom en objetos 3D
echo   - Click en botones para navegar entre escenas
echo   - Presione Ctrl+C para detener el servidor
echo.
call npm run dev
pause
