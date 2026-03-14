# Content Automation

Sistema de generación de contenido con IA y búsqueda web.

## Requisitos

- Python 3.8+

## Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/Bobiptus/ai-content-generator.git
cd ai-content-generator
```

2. **Crear entorno virtual (recomendado):**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno:**

Copia el archivo `.env.example` a `.env` y añade tus API keys:

```bash
copy .env.example .env
```

Edita `.env` y añade tus keys:

- **GROQ_API_KEY**: Obtén en https://console.groq.com
- **TAVILY_API_KEY**: Obtén en https://tavily.com (1000 búsquedas/mes gratis)
- **GOOGLE_API_KEY** (opcional): Obtén en https://aistudio.google.com/app/apikey

## Uso

```bash
python generate_article.py
```

El sistema te pedirá:
1. El tema del artículo
2. Si quieres buscar información actualizada en la web
3. El tono del artículo (profesional, casual, técnico)

## Estructura del Proyecto

```
content-automation/
├── src/
│   ├── agents/
│   │   ├── research_agent.py      # Agente de búsqueda web
│   │   └── content_generator.py  # Generador de artículos
│   ├── services/
│   │   └── cache_service.py      # Cache con TTL de 24h
├── generate_article.py           # Script principal
└── requirements.txt               # Dependencias
```

## Características

- Búsqueda web con Tavily API
- Cache de búsquedas (24 horas)
- Múltiples tonos de escritura
- Generación de artículos completos con outline, introducción, secciones y conclusión

## Licencia

MIT
