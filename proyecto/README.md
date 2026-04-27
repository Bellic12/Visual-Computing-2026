# Simulador de Parqueadero Inteligente

Este proyecto es una base de prueba para un sistema de detección de espacios de parqueadero con una interfaz 3D en el frontend y una API en el backend.

La idea es simple: el backend expone el estado de los espacios y calcula una ruta óptima hacia el espacio libre disponible. El frontend consume ese estado y lo muestra en una escena 3D para simular un parqueadero virtual.

## Estructura

- `backend/`: API en FastAPI con la lógica de espacios, ocupación simulada y ruta óptima.
- `frontend/`: Aplicación React + Vite con visualización 3D y panel de estado.

## Requisitos

- Python 3.12 o superior
- Node.js 18 o superior
- `pnpm` instalado

## Cómo ejecutar

### 1. Levantar el backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate.fish
pip install -r requirements.txt
cd src
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### 2. Levantar el frontend

En otra terminal:

```bash
cd frontend
pnpm install
pnpm dev
```

### 3. Abrir la aplicación

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Health check: `http://localhost:8000/health`
- Estado del parqueadero: `http://localhost:8000/estado`

## Variables opcionales

Si el frontend necesita apuntar a otra API, puedes definir:

```bash
VITE_API_URL=http://127.0.0.1:8000
```

## Qué muestra

- Cantidad de espacios ocupados y libres
- Un espacio libre sugerido como destino
- La ruta óptima desde una entrada del parqueadero
- Una escena 3D simulada para visualizar el layout

## Notas

- La ocupación está simulada para pruebas.
- La arquitectura está separada en módulos para facilitar que la detección, la ocupación y la navegación evolucionen por separado.
