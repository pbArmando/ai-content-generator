# AI Content Generator - Interfaz Web

## Estructura del Proyecto

```
ai-content-generator/
├── backend/              # FastAPI (Python)
│   ├── main.py          # Entry point
│   ├── api/             # Endpoints
│   └── services/        # Lógica de negocio
├── frontend/             # React + Vite
│   ├── src/
│   │   ├── components/  # Componentes React
│   │   └── pages/      # Páginas
│   └── package.json
├── src/                 # Agentes original
└── start-dev.bat        # Iniciar ambos servidores
```

## Setup

### 1. Instalar dependencias del backend
```bash
pip install -r backend/requirements.txt
```

### 2. Instalar dependencias del frontend
```bash
cd frontend
npm install
```

### 3. Configurar variables de entorno
Crear `.env` en la raíz con:
```
GROQ_API_KEY=tu_api_key
TAVILY_API_KEY=tu_api_key
CLOUDFLARE_ACCOUNT_ID=tu_account_id
CLOUDFLARE_API_TOKEN=tu_api_token
```

### 4. Ejecutar

Opción A - Usar el script:
```bash
start-dev.bat
```

Opción B - Manual:
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

## Acceder
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Tecnologías
- **Backend**: FastAPI (Python)
- **Frontend**: React + Vite
- **APIs**: Groq (LLM), Tavily (búsqueda), Cloudflare (imágenes)
