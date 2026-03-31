"""
ImageAgent - Generación de imágenes con Google Gemini
Reemplaza Cloudflare Workers AI
"""

import os
import sys
import time
import json
from typing import Optional, Dict, Any
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class ImageAgent:
    """
    Agente para generar imágenes usando Google Gemini (gemini-2.5-flash-image)
    Costo: $0.039/imagen (gratis con free tier)
    """
    
    def __init__(self, output_dir: str = "outputs/images", max_retries: int = 3):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_retries = max_retries
        
        # Cargar Google API
        self.api_key = os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            print("[WARN] GOOGLE_API_KEY not found. Images disabled.")
            self.client = None
        else:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai
                # Usar modelo de generación de imágenes
                self.model = 'gemini-2.5-flash-image-preview-05-20'
                print("[INFO] ImageAgent con Gemini API configurado")
            except ImportError:
                print("[WARN] google-generativeai no instalado. Images disabled.")
                self.client = None
        
        # Cargar PromptAgent y QA
        try:
            from agents.prompt_agent import PromptAgent
            from agents.qa_agent import ContentSecurityAgent
            self.prompt_agent = PromptAgent()
            self.qa_agent = ContentSecurityAgent()
        except ImportError:
            self.prompt_agent = None
            self.qa_agent = None
    
    def generate(self, prompt: str, width: int = 1024, height: int = 1024) -> Dict[str, Any]:
        """
        Genera una imagen usando Google Gemini
        """
        if not self.client:
            return {'success': False, 'error': 'Google API not configured', 'prompt': prompt}
        
        for attempt in range(self.max_retries):
            try:
                safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_prompt = safe_prompt.replace(' ', '_')
                filename = f"image_{safe_prompt}_{int(time.time())}.png"
                filepath = self.output_dir / filename
                
                print(f"  [Gemini Image] Generando: {prompt[:50]}...")
                
                # Generar imagen con Gemini
                response = self.client.generate_content(
                    self.model,
                    generation_config={
                        'response_modalities': ['TEXT', 'IMAGE']
                    }
                )
                
                # Buscar la imagen en la respuesta
                image_data = None
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        break
                
                if image_data:
                    with open(filepath, 'wb') as f:
                        f.write(image_data)
                    
                    return {
                        'success': True,
                        'filepath': str(filepath),
                        'model': self.model,
                        'prompt': prompt,
                        'size': f"{width}x{height}"
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No image in response',
                        'prompt': prompt
                    }
                    
            except Exception as e:
                error_msg = str(e)
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"  [Gemini Image] Error, esperando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                return {
                    'success': False,
                    'error': error_msg,
                    'prompt': prompt
                }
        
        return {'success': False, 'error': 'Max retries exceeded', 'prompt': prompt}
    
    def generate_for_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera imagen para un artículo basándose en su contenido.
        """
        # Generar prompt con PromptAgent
        if self.prompt_agent:
            prompt = self.prompt_agent.generate_article_prompt(article)
            print(f"  [QA] Prompt generado por PromptAgent")
        else:
            topic = article.get('topic', '')
            title = article.get('title', '')
            prompt = f"A beautiful and professional blog article cover about '{topic}'. Title: '{title}'. Modern style, clean design, high quality"
        
        # Revisar prompt con QA
        if self.qa_agent:
            from agents.qa_agent import QAReport
            qa_report = QAReport()
            
            if hasattr(self.qa_agent, 'review_image_prompt'):
                qa_report = self.qa_agent.review_image_prompt(prompt, article.get('topic', ''))
                
                if qa_report.findings:
                    print(f"  [QA] Hallazgos: {len(qa_report.findings)}")
                    for f in qa_report.findings:
                        print(f"     - {f['severity'].upper()}: {f['message']}")
                    
                    if hasattr(self.qa_agent, 'optimize_prompt'):
                        prompt = self.qa_agent.optimize_prompt(prompt, qa_report)
                        print(f"  [QA] Prompt optimizado")
                else:
                    print(f"  [QA] Prompt aprobado")
        
        return self.generate(prompt=prompt, width=1024, height=1024)
    
    def generate_social_post(self, article: Dict[str, Any], platform: str = "instagram") -> Dict[str, Any]:
        """
        Genera imagen para post de redes sociales.
        """
        sizes = {
            'instagram': (1080, 1080),
            'twitter': (1200, 675),
            'facebook': (1200, 630),
            'linkedin': (1200, 627)
        }
        
        width, height = sizes.get(platform, (1080, 1080))
        
        # Generar prompt
        if self.prompt_agent:
            prompt = self.prompt_agent.generate_social_prompt(article, platform)
        else:
            topic = article.get('topic', '')
            prompt = f"Social media post image about '{topic}'. Platform: {platform}. Eye-catching, modern design"
        
        # Revisar con QA
        if self.qa_agent:
            from agents.qa_agent import QAReport
            qa_report = QAReport()
            topic = article.get('topic', '')
            
            if hasattr(self.qa_agent, 'review_image_prompt'):
                qa_report = self.qa_agent.review_image_prompt(prompt, topic)
                
                if qa_report.findings:
                    for f in qa_report.findings:
                        print(f"     - {f['severity'].upper()}: {f['message']}")
                    
                    if hasattr(self.qa_agent, 'optimize_prompt'):
                        prompt = self.qa_agent.optimize_prompt(prompt, qa_report, topic)
                        print(f"     [QA] Prompt corregido")
        
        return self.generate(prompt=prompt, width=width, height=height)


def main():
    from agents.prompt_agent import PromptAgent
    
    agent = ImageAgent()
    print("Testing ImageAgent con Gemini...")
    
    test_article = {
        'topic': 'seguridad laboral en México',
        'title': 'La Importancia de la Seguridad Laboral en las Empresas Mexicanas',
        'introduction': 'La seguridad laboral es fundamental...',
        'conclusion': 'En conclusión, priorizar la seguridad...'
    }
    
    result = agent.generate_for_article(test_article)
    
    if result['success']:
        print(f"SUCCESS: {result['filepath']}")
        print(f"Prompt usado: {result['prompt']}")
    else:
        print(f"FAILED: {result.get('error')}")


if __name__ == "__main__":
    main()