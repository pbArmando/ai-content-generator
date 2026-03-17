import os
import sys
from typing import Dict, List, Any
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
load_dotenv()


class SocialMediaAgent:
    """
    Agente para generar contenido de redes sociales desde un artículo
    """
    
    PLATFORMS = {
        'twitter': {
            'name': 'Twitter/X',
            'max_length': 280,
            'hashtags': True,
            'emoji': True
        },
        'linkedin': {
            'name': 'LinkedIn',
            'max_length': 3000,
            'hashtags': True,
            'emoji': True
        },
        'instagram': {
            'name': 'Instagram',
            'max_length': 2200,
            'hashtags': True,
            'emoji': True
        },
        'facebook': {
            'name': 'Facebook',
            'max_length': 63206,
            'hashtags': True,
            'emoji': True
        }
    }
    
    def __init__(self):
        self.client = None
        self.model_name = None
        self._setup()
    
    def _setup(self):
        try:
            from groq import Groq
            api_key = os.getenv('GROQ_API_KEY')
            if api_key:
                self.client = Groq(api_key=api_key)
                self.model_name = "llama-3.3-70b-versatile"
        except:
            pass
    
    def generate(self, article: Dict[str, Any], platform: str = 'twitter') -> Dict[str, Any]:
        """
        Genera un post de redes sociales desde un artículo
        """
        if platform not in self.PLATFORMS:
            platform = 'twitter'
        
        config = self.PLATFORMS[platform]
        
        if not self.client:
            return {
                'success': False,
                'error': 'No hay cliente LLM disponible',
                'platform': platform
            }
        
        topic = article.get('topic', '')
        title = article.get('title', '')
        introduction = article.get('introduction', '')[:500]
        
        prompt = self._build_prompt(topic, title, introduction, platform, config)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            return {
                'success': True,
                'content': content,
                'platform': platform,
                'topic': topic
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': platform
            }
    
    def _build_prompt(self, topic: str, title: str, intro: str, platform: str, config: Dict) -> str:
        if platform == 'twitter':
            return f"""Genera un tweet interesante sobre "{topic}" basado en este artículo:
            
Título: {title}
Introducción: {intro}

Requisitos:
- Máximo 280 caracteres
- Include un call-to-action
- Incluye 1-2 hashtags relevantes
- Incluye emoji si es apropiado
- Incluye URL placeholder: [LINK]"""

        elif platform == 'linkedin':
            return f"""Genera un post profesional para LinkedIn sobre "{topic}" basado en:

Título: {title}
Introducción: {intro}

Requisitos:
- Tono profesional pero cercano
- Comparte una reflexión personal
- Incluye 3-5 hashtags profesionales
- Estructura: hook -> contenido -> call-to-action
- Incluye "Leer más" link placeholder: [LINK]"""

        elif platform == 'instagram':
            return f"""Genera un caption para Instagram sobre "{topic}":

Título: {title}
Introducción: {intro}

Requisitos:
- Tono amigable y visual
- Primera línea debe ser catchy (hook)
- Incluye 5-10 hashtags relevantes
- Incluye emoji
- Incluye "Link in bio" placeholder: [LINK]"""

        else:  # facebook
            return f"""Genera un post para Facebook sobre "{topic}":

Título: {title}
Introducción: {intro}

Requisitos:
- Tono conversacional
- Incluye preguntas para generar engagement
- 3-5 hashtags
- Incluye link placeholder: [LINK]"""

    def generate_all(self, article: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Genera posts para todas las plataformas
        """
        results = {}
        
        for platform in self.PLATFORMS.keys():
            result = self.generate(article, platform)
            results[platform] = result
        
        return results


def main():
    """Test del agente"""
    agent = SocialMediaAgent()
    
    test_article = {
        'topic': 'Python programming',
        'title': 'Aprende Python en 2025',
        'introduction': 'Python es uno de los lenguajes de programación más populares del mundo...'
    }
    
    print("Generando posts de prueba...")
    
    result = agent.generate(test_article, 'twitter')
    
    if result['success']:
        print(f"Twitter: {result['content']}")
    else:
        print(f"Error: {result.get('error')}")


if __name__ == "__main__":
    main()
