import os
import sys
import time
from dotenv import load_dotenv

# Agregar src al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

load_dotenv()

try:
    from services.cache_service import CacheService
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

try:
    from agents.research_agent import ResearchAgent
    RESEARCH_AVAILABLE = True
except ImportError:
    RESEARCH_AVAILABLE = False

# Intentar importar APIs (primero Groq, luego Google)
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError as e:
    GROQ_AVAILABLE = False
    print(f"DEBUG: Error al importar Groq: {e}")

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class ContentGenerator:
    """
    Clase para generar contenido usando Groq o Google Gemini
    """
    
    def __init__(self, provider="groq", enable_research=False):
        """
        Inicializa el generador
        
        Args:
            provider (str): 'groq' o 'google'
            enable_research (bool): Si True, habilita búsqueda web antes de generar
        """
        self.provider = provider
        self.enable_research = enable_research
        self.last_request_time = 0
        self.min_delay = 3  # 3 segundos entre requests
        self.research_agent = None
        
        if enable_research and RESEARCH_AVAILABLE:
            try:
                self.research_agent = ResearchAgent()
                print("✅ Búsqueda web habilitada (Tavily)")
            except Exception as e:
                print(f"⚠️ No se pudo inicializar investigación: {e}")
        
        # Configurar según el proveedor
        if provider == "groq" and GROQ_AVAILABLE:
            self._setup_groq()
        elif provider == "google" and GOOGLE_AVAILABLE:
            self._setup_google()
        else:
            raise ValueError(f"Proveedor '{provider}' no disponible o no instalado")
    
    def _setup_groq(self):
        """Configura Groq API"""
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("No se encontró GROQ_API_KEY en el archivo .env")
        
        self.client = Groq(api_key=api_key)
        self.model_name = "llama-3.3-70b-versatile"  # Modelo de Groq
        print("✅ Usando Groq API (Llama 3.3 70B)")
    
    def _setup_google(self):
        """Configura Google Gemini API"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("No se encontró GOOGLE_API_KEY en el archivo .env")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-image')
        print("✅ Usando Google Gemini API")
    
    def _wait_if_needed(self):
        """Espera el tiempo necesario para no exceder rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            wait_time = self.min_delay - time_since_last
            print(f"⏳ Esperando {wait_time:.1f} segundos...")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def _generate_with_groq(self, prompt):
        """Genera contenido con Groq"""
        try:
            self._wait_if_needed()
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _generate_with_google(self, prompt):
        """Genera contenido con Google"""
        try:
            self._wait_if_needed()
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _generate(self, prompt):
        """Genera contenido usando el proveedor configurado"""
        if self.provider == "groq":
            return self._generate_with_groq(prompt)
        else:
            return self._generate_with_google(prompt)
    
    def generate_article_outline(self, topic, research_data=None):
        """
        Genera un outline (esquema) para un artículo
        
        Args:
            topic (str): El tema del artículo
            research_data (dict): Datos de investigación opcionales
            
        Returns:
            str: El outline generado
        """
        research_context = ""
        if research_data and self.research_agent:
            research_context = self.research_agent.format_for_prompt(research_data)
        
        if research_context:
            prompt = f"""Crea un outline detallado para un artículo de blog sobre: {topic}

INFORMACIÓN ACTUALIZADA DE LA INVESTIGACIÓN:
{research_context}

El outline debe incluir:
1. Un título atractivo basado en la información más reciente
2. Una introducción breve (2-3 oraciones)
3. 4-5 secciones principales con subtítulos
4. Una conclusión

Formato:
TÍTULO: [título aquí]

INTRODUCCIÓN:
[texto de introducción]

SECCIONES:
1. [Subtítulo 1]
   - Puntos clave a cubrir
2. [Subtítulo 2]
   - Puntos clave a cubrir
[etc...]

CONCLUSIÓN:
[idea para la conclusión]"""
        else:
            prompt = f"""Crea un outline detallado para un artículo de blog sobre: {topic}

El outline debe incluir:
1. Un título atractivo
2. Una introducción breve (2-3 oraciones)
3. 4-5 secciones principales con subtítulos
4. Una conclusión

Formato:
TÍTULO: [título aquí]

INTRODUCCIÓN:
[texto de introducción]

SECCIONES:
1. [Subtítulo 1]
   - Puntos clave a cubrir
2. [Subtítulo 2]
   - Puntos clave a cubrir
[etc...]

CONCLUSIÓN:
[idea para la conclusión]"""
        
        return self._generate(prompt)
    
    def generate_introduction(self, topic, outline):
        """
        Genera una introducción atractiva
        
        Args:
            topic (str): El tema del artículo
            outline (str): El outline del artículo
            
        Returns:
            str: La introducción generada
        """
        prompt = f"""Basándote en este outline para un artículo sobre "{topic}":

{outline}

Escribe una introducción atractiva de 2-3 párrafos que:
1. Capture la atención del lector
2. Explique de qué tratará el artículo
3. Mencione el valor para el lector
4. Use tono conversacional pero profesional

NO incluyas títulos, solo el texto de la introducción."""
        
        return self._generate(prompt)
    
    def generate_conclusion(self, topic, article_content):
        """
        Genera una conclusión para el artículo
        
        Args:
            topic (str): El tema del artículo
            article_content (str): El contenido del artículo
            
        Returns:
            str: La conclusión generada
        """
        prompt = f"""Basándote en este artículo sobre "{topic}":

{article_content[:1000]}...

Escribe una conclusión de 2 párrafos que:
1. Resuma los puntos clave
2. Proporcione un llamado a la acción
3. Deje al lector con una idea poderosa

NO incluyas títulos, solo el texto de la conclusión."""
        
        return self._generate(prompt)
    
    def parse_outline_sections(self, outline):
        """
        Extrae las secciones del outline
        
        Args:
            outline (str): El outline generado
            
        Returns:
            list: Lista de diccionarios con título y puntos clave de cada sección
        """
        sections = []
        lines = outline.split('\n')
        
        in_sections = False
        current_section = None
        current_points = []
        
        for line in lines:
            line = line.strip()
            
            # Detectar inicio de secciones
            if 'SECCIONES:' in line or 'SECTIONS:' in line:
                in_sections = True
                continue
            
            # Detectar fin de secciones
            if in_sections and ('CONCLUSIÓN:' in line or 'CONCLUSION:' in line):
                # Guardar última sección si existe
                if current_section:
                    sections.append({
                        'title': current_section,
                        'points': ' '.join(current_points)
                    })
                break
            
            if in_sections and line:
                # Detectar nuevo subtítulo (empieza con número)
                if line[0].isdigit() and '.' in line[:3]:
                    # Guardar sección anterior si existe
                    if current_section:
                        sections.append({
                            'title': current_section,
                            'points': ' '.join(current_points)
                        })
                    
                    # Limpiar el título (quitar número y guiones)
                    current_section = line.split('.', 1)[1].strip()
                    current_section = current_section.replace('[', '').replace(']', '')
                    current_points = []
                
                # Detectar puntos clave (empiezan con -)
                elif line.startswith('-'):
                    point = line[1:].strip()
                    current_points.append(point)
        
        # Si no se encontraron secciones con el formato esperado, crear secciones genéricas
        if not sections:
            sections = [
                {'title': 'Conceptos Fundamentales', 'points': 'Explicar los conceptos básicos y fundamentales del tema'},
                {'title': 'Características Principales', 'points': 'Detallar las características más importantes'},
                {'title': 'Beneficios y Aplicaciones', 'points': 'Describir beneficios prácticos y casos de uso'},
                {'title': 'Mejores Prácticas', 'points': 'Compartir recomendaciones y consejos prácticos'}
            ]
        
        return sections
    
    def generate_section_content(self, section_title, section_points, topic, tone):
        """
        Genera el contenido completo de una sección
        
        Args:
            section_title (str): Título de la sección
            section_points (str): Puntos clave a cubrir
            topic (str): Tema general del artículo
            tone (str): Tono del artículo
            
        Returns:
            str: Contenido de la sección
        """
        tone_instructions = {
            'profesional': 'Usa lenguaje profesional, claro y preciso. Incluye datos cuando sea posible.',
            'casual': 'Usa lenguaje conversacional, cercano y amigable. Incluye ejemplos cotidianos.',
            'técnico': 'Usa terminología técnica precisa. Incluye detalles específicos y ejemplos técnicos.'
        }
        
        prompt = f"""Escribe el contenido para esta sección de un artículo sobre "{topic}":

**Título de la sección:** {section_title}

**Puntos clave a cubrir:** {section_points}

**Requisitos:**
- Escribe 3-4 párrafos sustanciales (150-250 palabras)
- {tone_instructions.get(tone, tone_instructions['profesional'])}
- Incluye ejemplos concretos y específicos
- Usa subtítulos secundarios si es necesario (###)
- Sé informativo y útil para el lector
- NO repitas el título de la sección al inicio
- Comienza directamente con el contenido

Genera contenido de alta calidad, bien estructurado y fácil de leer."""
        
        return self._generate(prompt)

    def generate_full_article(self, topic, tone="profesional", include_sections=True, use_research=False):
        """
        Genera un artículo completo sobre un tema
        
        Args:
            topic (str): El tema del artículo
            tone (str): El tono deseado (profesional, casual, técnico)
            include_sections (bool): Si True, genera el cuerpo completo del artículo
            use_research (bool): Si True, busca información actualizada antes de generar
            
        Returns:
            dict: Diccionario con todas las partes del artículo
        """
        research_data = None
        
        if use_research and self.research_agent:
            print("\n🔍 Paso 0/5: Buscando información actualizada...")
            try:
                research_data = self.research_agent.research_topic(topic)
                if research_data.get('results') or research_data.get('answer'):
                    print(f"   ✅ Información encontrada de {len(research_data.get('sources', []))} fuentes")
                else:
                    print("   ⚠️ No se encontró información, continuando sin investigación")
            except Exception as e:
                print(f"   ⚠️ Error en búsqueda: {e}")
        
        print("\n📋 Paso 1/5: Generando outline...")
        outline = self.generate_article_outline(topic, research_data)
        
        if outline.startswith("Error"):
            return {"error": outline}
        
        print("✅ Outline generado")
        
        # Extraer título
        title = "Sin título"
        for line in outline.split('\n'):
            if line.strip().startswith('TÍTULO:'):
                title = line.replace('TÍTULO:', '').strip()
                break
        
        print(f"\n📝 Paso 2/5: Generando introducción...")
        introduction = self.generate_introduction(topic, outline)
        
        if introduction.startswith("Error"):
            return {"error": introduction}
            
        print("✅ Introducción generada")
        
        # Generar secciones del cuerpo
        sections = []
        
        if include_sections:
            print(f"\n📚 Paso 3/5: Generando secciones del artículo...")
            
            # Extraer secciones del outline
            outline_sections = self.parse_outline_sections(outline)
            print(f"   Secciones a generar: {len(outline_sections)}")
            
            for i, section_info in enumerate(outline_sections, 1):
                print(f"\n   📄 Generando sección {i}/{len(outline_sections)}: {section_info['title']}")
                
                content = self.generate_section_content(
                    section_info['title'],
                    section_info['points'],
                    topic,
                    tone
                )
                
                if not content.startswith("Error"):
                    sections.append({
                        'title': section_info['title'],
                        'content': content
                    })
                    words = len(content.split())
                    print(f"   ✅ Sección completada (~{words} palabras)")
                else:
                    print(f"   ⚠️ Error en sección: {content}")
        else:
            print(f"\n⏭️ Paso 3/5: Saltando generación de secciones...")
        
        print(f"\n🔚 Paso 4/5: Generando conclusión...")
        
        # Usar introducción + primeras secciones para contexto
        article_context = introduction
        if sections:
            article_context += "\n\n" + sections[0]['content'][:500]
        
        conclusion = self.generate_conclusion(topic, article_context)
        
        if conclusion.startswith("Error"):
            return {"error": conclusion}
            
        print("✅ Conclusión generada")
        
        # Calcular palabras totales
        intro_words = len(introduction.split())
        sections_words = sum(len(s['content'].split()) for s in sections)
        conclusion_words = len(conclusion.split())
        total_words = intro_words + sections_words + conclusion_words
        
        print(f"\n✅ Paso 5/5: Artículo completo generado")
        print(f"   📊 Palabras totales: {total_words}")
        
        article = {
            "title": title,
            "topic": topic,
            "tone": tone,
            "outline": outline,
            "introduction": introduction,
            "sections": sections,
            "conclusion": conclusion,
            "word_count": total_words,
            "research_data": research_data
        }
        
        return article