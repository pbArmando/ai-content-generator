import os
import sys
import time
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

load_dotenv()


class LLMAgent:
    """Clase base para agentes LLM - optimizada para menor uso de tokens"""
    
    def __init__(self, provider: str = "groq"):
        self.provider = provider
        self.last_request_time = 0
        self.min_delay = 1.5  # Optimizado: 1.5s en lugar de 3s
        self.client = None
        self.model_name = None
        self._setup_provider()
    
    def _setup_provider(self):
        if self.provider == "groq":
            from groq import Groq
            api_key = os.getenv('GROQ_API_KEY')
            if api_key:
                self.client = Groq(api_key=api_key)
                self.model_name = "llama-3.3-70b-versatile"
        elif self.provider == "google":
            import google.generativeai as genai
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash-image')
    
    def _wait_if_needed(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_delay:
            time.sleep(self.min_delay - time_since_last)
        self.last_request_time = time.time()
    
    def generate(self, prompt: str, max_tokens: int = 1500) -> str:
        """Método genérico para generar contenido - optimizado"""
        if not self.client and not hasattr(self, 'model'):
            return "Error: No hay cliente LLM disponible"
        
        try:
            self._wait_if_needed()
            
            if self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            else:
                response = self.model.generate_content(prompt)
                return response.text
        except Exception as e:
            return f"Error: {str(e)}"


class OutlineAgent(LLMAgent):
    """Agente especializado en generar outlines - usa menos tokens"""
    
    PROMPT_TEMPLATE = """Genera un outline para un artículo sobre: {topic}

Requisitos:
- 1 título atractivo
- 1 introducción de 2-3 oraciones
- 4-5 secciones con subtítulos
- 1 conclusión

Formato:
TÍTULO: [título]
INTRODUCCIÓN: [texto]
SECCIONES:
1. [subtítulo]
2. [subtítulo]
3. [subtítulo]
4. [subtítulo]
CONCLUSIÓN: [texto]"""

    def generate(self, topic: str, research_context: str = "") -> str:
        prompt = self.PROMPT_TEMPLATE.format(topic=topic)
        if research_context:
            prompt += f"\n\nINFO ACTUALIZADA: {research_context[:500]}"
        return super().generate(prompt, max_tokens=800)


class IntroductionAgent(LLMAgent):
    """Agente especializado en introducciones"""
    
    PROMPT_TEMPLATE = """Escribe una introducción de 2-3 párrafos para un artículo sobre "{topic}" con este outline:

{outline}

Requisitos:
- Captura la atención
- Explica de qué trata el artículo
- Menciona el valor para el lector
- Tono: {tone}"""

    def generate(self, topic: str, outline: str, tone: str = "profesional") -> str:
        prompt = self.PROMPT_TEMPLATE.format(topic=topic, outline=outline[:1000], tone=tone)
        return super().generate(prompt, max_tokens=400)


class SectionAgent(LLMAgent):
    """Agente especializado en secciones de artículo"""
    
    TONE_INSTRUCTIONS = {
        'profesional': 'Lenguaje profesional y preciso. Incluye datos.',
        'casual': 'Lenguaje conversacional. Ejemplos cotidianos.',
        'técnico': 'Terminología técnica. Ejemplos especializados.'
    }
    
    def generate(self, section_title: str, section_points: str, topic: str, tone: str = "profesional") -> str:
        prompt = f"""Sección sobre "{topic}"

Título: {section_title}
Puntos: {section_points}

Requisitos:
- 3-4 párrafos (150-250 palabras)
- {self.TONE_INSTRUCTIONS.get(tone, self.TONE_INSTRUCTIONS['profesional'])}
- Ejemplos concretos
- NO repitas el título"""

        return super().generate(prompt, max_tokens=600)


class ConclusionAgent(LLMAgent):
    """Agente especializado en conclusiones"""
    
    PROMPT_TEMPLATE = """Escribe una conclusión de 2 párrafos para un artículo sobre "{topic}":

{content}

Requisitos:
- Resume los puntos clave
- Incluye llamado a la acción
-Deja una idea poderosa"""

    def generate(self, topic: str, article_content: str) -> str:
        prompt = self.PROMPT_TEMPLATE.format(topic=topic, content=article_content[:800])
        return super().generate(prompt, max_tokens=300)


class OrchestratorAgent:
    """Orquestador de agentes - coordina el flujo sin acumular contexto"""
    
    def __init__(self, provider: str = "groq"):
        self.outline_agent = OutlineAgent(provider)
        self.intro_agent = IntroductionAgent(provider)
        self.section_agent = SectionAgent(provider)
        self.conclusion_agent = ConclusionAgent(provider)
    
    def generate_article(self, topic: str, tone: str = "profesional", 
                        research_context: str = "") -> Dict[str, Any]:
        """Genera artículo completo con agentes independientes"""
        
        print("📋 Generando outline...")
        outline = self.outline_agent.generate(topic, research_context)
        
        if outline.startswith("Error"):
            return {"error": outline}
        
        title = self._extract_title(outline)
        
        print("📝 Generando introducción...")
        introduction = self.intro_agent.generate(topic, outline, tone)
        
        if introduction.startswith("Error"):
            return {"error": introduction}
        
        print("📚 Generando conclusión...")
        conclusion = self.conclusion_agent.generate(topic, introduction + outline[:500])
        
        if conclusion.startswith("Error"):
            return {"error": conclusion}
        
        word_count = (
            len(introduction.split()) + 
            len(conclusion.split())
        )
        
        return {
            "title": title,
            "topic": topic,
            "tone": tone,
            "outline": outline,
            "introduction": introduction,
            "conclusion": conclusion,
            "word_count": word_count,
            "sections": []  # Simplified: sin secciones individuales
        }
    
    def _extract_title(self, outline: str) -> str:
        for line in outline.split('\n'):
            if line.strip().startswith('TÍTULO:'):
                return line.replace('TÍTULO:', '').strip()
        return "Sin título"
