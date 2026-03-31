"""
VideoAgent - Generación de videos con Google Veo 3.1
Usa la API de Gemini para generar videos
"""

import os
import sys
import time
import json
from typing import Optional, Dict, Any
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class VideoAgent:
    """
    Agente para generar videos usando Google Veo 3.1
    Costo: $0.15/seg (Fast) - $0.40/seg (Standard)
    """
    
    def __init__(self, output_dir: str = "outputs/videos", max_retries: int = 3):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_retries = max_retries
        
        # Configuración de calidad
        self.quality = 'fast'  # 'fast' o 'standard'
        
        # Cargar Google API
        self.api_key = os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            print("[WARN] GOOGLE_API_KEY not found. Videos disabled.")
            self.client = None
        else:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai
                # Modelo de video
                self.model = 'veo-3.1-generate-2.0'
                print("[INFO] VideoAgent con Veo 3.1 configurado")
            except ImportError:
                print("[WARN] google-generativeai no instalado. Videos disabled.")
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
    
    def generate(self, prompt: str, duration: int = 5) -> Dict[str, Any]:
        """
        Genera un video usando Veo 3.1
        
        Args:
            prompt: Descripción del video
            duration: Duración en segundos (5-8 segundos)
        """
        if not self.client:
            return {'success': False, 'error': 'Google API not configured', 'prompt': prompt}
        
        if duration > 8:
            duration = 8  # Máximo 8 segundos
        if duration < 5:
            duration = 5  # Mínimo 5 segundos
        
        for attempt in range(self.max_retries):
            try:
                safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_prompt = safe_prompt.replace(' ', '_')
                filename = f"video_{safe_prompt}_{int(time.time())}.mp4"
                filepath = self.output_dir / filename
                
                print(f"  [Veo Video] Generando video de {duration}s: {prompt[:50]}...")
                
                # Generar video con Veo
                # Nota: La API de Veo requiere prompt más detallado
                enhanced_prompt = f"{prompt}. Make it dynamic, smooth motion, high quality, professional."
                
                response = self.client.generate_content(
                    self.model,
                    generation_config={
                        'response_modalities': ['VIDEO'],
                        'video_duration': duration
                    }
                )
                
                # Buscar el video en la respuesta
                video_data = None
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        video_data = part.inline_data.data
                        break
                
                if video_data:
                    with open(filepath, 'wb') as f:
                        f.write(video_data)
                    
                    return {
                        'success': True,
                        'filepath': str(filepath),
                        'model': self.model,
                        'prompt': prompt,
                        'duration': duration,
                        'quality': self.quality
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No video in response',
                        'prompt': prompt
                    }
                    
            except Exception as e:
                error_msg = str(e)
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 10
                    print(f"  [Veo Video] Error, esperando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                return {
                    'success': False,
                    'error': error_msg,
                    'prompt': prompt
                }
        
        return {'success': False, 'error': 'Max retries exceeded', 'prompt': prompt}
    
    def generate_for_article(self, article: Dict[str, Any], duration: int = 5) -> Dict[str, Any]:
        """
        Genera video promocional para un artículo.
        """
        topic = article.get('topic', '')
        title = article.get('title', '')
        
        # Generar prompt para video
        prompt = f"Dynamic video showing {topic}. Title: {title}. Smooth camera movement, professional editing, high quality, no text overlays, b-roll style footage"
        
        # Revisar con QA
        if self.qa_agent:
            from agents.qa_agent import QAReport
            qa_report = QAReport()
            
            if hasattr(self.qa_agent, 'review_image_prompt'):
                qa_report = self.qa_agent.review_image_prompt(prompt, topic)
                
                if qa_report.findings:
                    print(f"  [QA Video] Hallazgos: {len(qa_report.findings)}")
                    for f in qa_report.findings:
                        print(f"     - {f['severity'].upper()}: {f['message']}")
                    
                    if hasattr(self.qa_agent, 'optimize_prompt'):
                        prompt = self.qa_agent.optimize_prompt(prompt, qa_report)
                else:
                    print(f"  [QA Video] Prompt aprobado")
        
        return self.generate(prompt=prompt, duration=duration)
    
    def generate_social_video(self, article: Dict[str, Any], platform: str = "instagram", duration: int = 5) -> Dict[str, Any]:
        """
        Genera video corto para redes sociales.
        """
        topic = article.get('topic', '')
        
        # Prompts específicos por plataforma
        platform_prompts = {
            'instagram': f"Cinematic vertical video about {topic}. Trending style, vibrant colors, smooth motion, hook opening, professional",
            'twitter': f"Short impactful video about {topic}. Fast-paced, engaging, high energy, loop-friendly",
            'facebook': f"Professional video about {topic}. Clean visuals, smooth transitions, brand-friendly",
            'linkedin': f"Corporate video about {topic}. Professional, clean, business-appropriate, high quality"
        }
        
        prompt = platform_prompts.get(platform, platform_prompts['instagram'])
        
        print(f"  [Veo] Generando video para {platform}...")
        
        return self.generate(prompt=prompt, duration=duration)
    
    def set_quality(self, quality: str):
        """Cambiar calidad del video: 'fast' o 'standard'"""
        if quality in ['fast', 'standard']:
            self.quality = quality
            print(f"[INFO] Video quality set to: {quality}")
    
    def estimate_cost(self, duration: int) -> float:
        """Estimar costo del video"""
        if self.quality == 'fast':
            return duration * 0.15
        else:
            return duration * 0.40


def main():
    agent = VideoAgent()
    print("Testing VideoAgent con Veo 3.1...")
    
    test_article = {
        'topic': 'seguridad laboral en México',
        'title': 'La Importancia de la Seguridad Laboral'
    }
    
    # Estimar costo
    cost = agent.estimate_cost(5)
    print(f"Costo estimado para 5s: ${cost:.2f}")
    
    result = agent.generate_for_article(test_article, duration=5)
    
    if result['success']:
        print(f"SUCCESS: {result['filepath']}")
        print(f"Prompt usado: {result['prompt']}")
    else:
        print(f"FAILED: {result.get('error')}")


if __name__ == "__main__":
    main()