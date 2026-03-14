# Content Automation

Sistema de generación de contenido con IA y búsqueda web automática.

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación](#instalación)
3. [Configuración de API Keys](#configuración-de-api-keys)
4. [Ejecución](#ejecución)
5. [Estructura del Proyecto](#estructura-del-proyecto)
6. [Cómo Funciona](#cómo-funciona)
7. [Solución de Problemas](#solución-de-problemas)

---

## Requisitos Previos

### Software Necesario

| Software | Versión Mínima | Descripción |
|----------|----------------|--------------|
| Python | 3.8+ | Lenguaje de programación |
| Git | 2.0+ | Control de versiones |
| pip | 21.0+ | Gestor de paquetes Python |

### Verificar Instalación

```bash
# Verificar Python
python --version

# Verificar pip
pip --version

# Verificar Git
git --version
```

---

## Instalación

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/Bobiptus/ai-content-generator.git
cd ai-content-generator
```

### Paso 2: Crear Entorno Virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux / MacOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Actualizar pip (Recomendado)

```bash
python -m pip install --upgrade pip
```

### Paso 4: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 5: Verificar Instalación

```bash
# Verificar que las librerías están instaladas
pip list
```

Deberías ver:
- google-generativeai
- python-dotenv
- requests
- beautifulsoup4
- groq
- tavily
- httpx

---

## Configuración de API Keys

### Importante

**Cada usuario debe crear su propio archivo `.env` con sus API keys personales.** El archivo `.env` contiene claves privadas y **NO** debe compartirse.

### Paso 1: Copiar el Archivo de Ejemplo

**Windows:**
```bash
copy .env.example .env
```

**Linux / MacOS:**
```bash
cp .env.example .env
```

### Paso 2: Obtener las API Keys

#### GROQ_API_KEY (Requerida)

Groq ofrece acceso gratuito a modelos LLM de alta calidad.

1. Ve a https://console.groq.com
2. Crea una cuenta o inicia sesión
3. Ve a "API Keys"
4. Crea una nueva API Key
5. Copia la key y pégala en `.env`

**Ubicación en .env:**
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
```

#### TAVILY_API_KEY (Requerida para búsqueda web)

Tavily ofrece 1000 búsquedas/mes gratis.

1. Ve a https://tavily.com
2. Crea una cuenta o inicia sesión
3. Ve a tu perfil o sección de API
4. Copia tu API Key
5. Pégala en `.env`

**Ubicación en .env:**
```
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxx
```

#### GOOGLE_API_KEY (Opcional)

Solo necesaria si quieres usar Google Gemini como proveedor alternativo.

1. Ve a https://aistudio.google.com/app/apikey
2. Crea una nueva API Key
3. Copia y pega en `.env`

**Ubicación en .env:**
```
GOOGLE_API_KEY=AIzaxxxxxxxxxxxxxxxx
```

### Paso 3: Estructura Final del .env

Tu archivo `.env` debería verse así:

```env
GROQ_API_KEY=tu_groq_api_key_aqui
TAVILY_API_KEY=tu_tavily_api_key_aqui
GOOGLE_API_KEY=tu_google_api_key_aqui  # Opcional
```

---

## Ejecución

### Ejecutar el Programa

```bash
python generate_article.py
```

### Interfaz de Usuario

El programa te guiará paso a paso:

```
======================================================================
📰 GENERADOR DE ARTÍCULOS COMPLETOS CON IA
======================================================================

🔧 Inicializando sistema...
✅ Usando Groq API (Llama 3.3 70B)
✅ Sistema listo (con búsqueda web)

📝 Configuración del artículo:
----------------------------------------------------------------------
Tema del artículo: [INGRESA TU TEMA]
```

### Opciones Durante la Ejecución

1. **Tema del artículo:** Ingresa el tema sobre el cual quieres generar contenido

2. **Búsqueda web:**
   - `1` = Sí (recomendado - usa información actualizada de la web)
   - `2` = No (usa solo el conocimiento del modelo LLM)

3. **Tono del artículo:**
   - `1` = Profesional (lenguaje formal y técnico)
   - `2` = Casual (lenguaje amigable y conversacional)
   - `3` = Técnico (terminología especializada)

### Salida

Los artículos generados se guardan automáticamente en:
- `outputs/article_[tema]_[fecha].md` (Markdown)
- `outputs/article_[tema]_[fecha].txt` (Texto plano)

---

## Estructura del Proyecto

```
ai-content-generator/
├── .env                    # Variables de entorno (NO subir a git)
├── .env.example            # Plantilla de configuración
├── .gitignore             # Archivos ignorados por git
├── README.md              # Este archivo
├── requirements.txt        # Dependencias Python
├── generate_article.py    # Script principal
├── main.py                # Script alternativo (outline básico)
├── src/
│   ├── agents/
│   │   ├── research_agent.py      # Agente de búsqueda web
│   │   └── content_generator.py  # Generador de artículos
│   ├── services/
│   │   └── cache_service.py      # Cache con TTL de 24h
│   └── utils/
│       └── __init__.py
└── outputs/                       # Artículos generados
    ├── article_[tema]_[fecha].md
    └── article_[tema]_[fecha].txt
```

---

## Cómo Funciona

### Flujo de Ejecución

```
┌─────────────────┐
│ Usuario         │
│ (ingresa tema) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ContentGenerator│
└────────┬────────┘
         │
         ▼ (si búsqueda habilitada)
┌─────────────────┐     ┌──────────────────┐
│ ResearchAgent   │────▶│ Tavily API       │
│ (búsqueda web)  │     │ (resúmenes web)  │
└────────┬────────┘     └──────────────────┘
         │
         ▼ (resultados + cache)
┌─────────────────┐
│ LLM (Groq)     │
│ + información  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Outline         │
│ + Introducción │
│ + Secciones    │
│ + Conclusión   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Archivo .md    │
│ + .txt         │
└─────────────────┘
```

### Componentes

#### 1. ResearchAgent
- Realiza búsquedas en la web usando Tavily
- Extrae información relevante sobre el tema
- Guarda resultados en cache por 24 horas
- Evita búsquedas重复idas del mismo tema

#### 2. ContentGenerator
- Genera outline estructurado del artículo
- Escribe introducción atractiva
- Desarrolla cada sección con contenido sustancial
- Crea conclusión con llamado a la acción

#### 3. CacheService
- Almacena resultados de búsqueda
- TTL (Time To Live) de 24 horas
- Evita consumo innecesario de API
- Mejora velocidad de ejecución

### Proveedores LLM Soportados

| Proveedor | Modelo | Estado | Notas |
|-----------|--------|--------|-------|
| Groq | Llama 3.3 70B | ✅ Predeterminado | Rápido y gratuito |
| Google | Gemini 2.5 Flash | ✅ Opcional | Requiere API key |

---

## Solución de Problemas

### Error: "No module named 'dotenv'"

**Causa:** Las dependencias no se instalaron correctamente.

**Solución:**
```bash
pip install python-dotenv
```

### Error: "No se encontró GROQ_API_KEY"

**Causa:** Falta la API key en el archivo `.env`.

**Solución:**
1. Verifica que el archivo `.env` exista
2. Asegúrate de que la línea `GROQ_API_KEY=...` esté presente
3. Verifica que la API key sea correcta

### Error: "Tavily no está instalado"

**Causa:** La librería tavily no está instalada.

**Solución:**
```bash
pip install tavily>=1.0.0
```

### Error: "Rate limit exceeded"

**Causa:** Has excedido los límites de la API.

**Solución:**
- Espera 1 minuto para Groq
- Para Tavily: espera hasta el siguiente mes (1000 búsquedas/mes gratis)

### Error: "venv\Scripts\Activate no se reconoce"

**Causa:** Estás usando PowerShell con política de ejecución restringida.

**Solución:**
```powershell
# Opción 1: Cambiar a CMD
cmd /k venv\Scripts\activate.bat

# Opción 2: Habilitar scripts en PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### El programa no responde

**Causa:** La generación de contenido puede tomar 30-90 segundos.

**Solución:**
- Ten paciencia, es normal
- Verifica tu conexión a internet

### Verificar Configuración de APIs

Puedes probar que las APIs estén configuradas correctamente:

```bash
# Probar Groq
python -c "from groq import Groq; print('Groq OK')"

# Probar Tavily
python -c "from tavily import TavilyClient; print('Tavily OK')"
```

---

## Actualización del Proyecto

Para obtener la última versión:

```bash
git pull origin main
```

---

## Licencia

MIT

---

## Contribuciones

Las contribuciones son bienvenidas. Por favor, crea un fork del repositorio y envía un pull request.

---

## Soporte

Si tienes problemas:
1. Revisa la sección de [Solución de Problemas](#solución-de-problemas)
2. Busca en los issues de GitHub
3. Crea un nuevo issue si no encuentras solución
