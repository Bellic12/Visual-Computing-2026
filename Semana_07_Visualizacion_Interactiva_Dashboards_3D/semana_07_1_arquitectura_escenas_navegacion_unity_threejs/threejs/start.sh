#!/bin/bash
# Inicio Rápido - Proyecto de Arquitectura de Juego

echo "🎮 Taller 62 - Arquitectura de Juego, Escenas y Navegación"
echo "=========================================================="
echo ""
echo "📍 Ubicación actual: $(pwd)"
echo ""

# Check if node_modules exists
if [ -d "node_modules" ]; then
    echo "✅ Dependencias ya están instaladas"
else
    echo "📦 Instalando dependencias..."
    npm install
fi

echo ""
echo "🚀 Iniciando servidor de desarrollo..."
echo ""
echo "La aplicación estará disponible en: http://localhost:5173"
echo ""
echo "🎮 Escenas disponibles:"
echo "  • Menu Principal      → /"
echo "  • Juego Interactivo   → /juego"
echo "  • Créditos del Proyecto → /creditos"
echo ""
echo "💡 Tips:"
echo "  • Use el ratón para rotar y hacer zoom en objetos 3D"
echo "  • Click en botones para navegar entre escenas"
echo "  • Presione Ctrl+C para detener el servidor"
echo ""
npm run dev
