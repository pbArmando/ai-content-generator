import os
import sys
import time
import urllib.request
import ssl
import urllib.parse
from typing import Optional, Dict, Any
from pathlib import Path


class ImageAgent:
    """
    Agente para generar imágenes usando Pollinations API
    Gratis, sin API key necesaria
    """
    
    POLLINATIONS_URL = "https://image.pollinations.ai/prompt/"
    
    def __init__(self, output_dir: str = "outputs/images", max_retries: int = 3):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        self.max_retries = max_retries
    
    def generate(self, prompt: str, width: int = 1024, height: int = 1024, 
                 model: str = "flux", seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Genera una imagen a partir de un prompt
        """
        # Acortar prompt si es muy largo
        if len(prompt) > 100:
            prompt = prompt[:100]
        
        for attempt in range(self.max_retries):
            try:
                # Construir URL
                encoded_prompt = urllib.parse.quote(prompt)
                url = f"{self.POLLINATIONS_URL}{encoded_prompt}?width={width}&height={height}&nologo=true"
                
                if seed:
                    url += f"&seed={seed}"
                
                # Generar nombre de archivo
                safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_prompt = safe_prompt.replace(' ', '_')
                filename = f"image_{safe_prompt}_{int(time.time())}.png"
                filepath = self.output_dir / filename
                
                # Descargar imagen con headers
                print(f"  [Image] Generando: {prompt[:50]}...")
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=90, context=self.ctx) as response:
                    with open(filepath, 'wb') as f:
                        f.write(response.read())
                
                return {
                    'success': True,
                    'filepath': str(filepath),
                    'url': url,
                    'prompt': prompt,
                    'size': f"{width}x{height}"
                }
                
            except Exception as e:
                error_msg = str(e)
                if '429' in error_msg and attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"  [Image] Rate limit, esperando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                return {
                    'success': False,
                    'error': error_msg,
                    'prompt': prompt
                }
        
        return {'success': False, 'error': 'Max retries exceeded', 'prompt': prompt}
    
    def generate_for_article(self, topic: str, title: str) -> Dict[str, Any]:
        """
        Genera imagen para un artículo basándose en el tema
        """
        prompt = f"{topic} article cover, modern minimalist design"
        
        return self.generate(
            prompt=prompt,
            width=1024,
            height=1024
        )
    
    def generate_social_post(self, topic: str, platform: str = "instagram") -> Dict[str, Any]:
        """
        Genera imagen para post de redes sociales
        """
        sizes = {
            'instagram': (1080, 1080),
            'twitter': (1200, 675),
            'facebook': (1200, 630),
            'linkedin': (1200, 627)
        }
        
        width, height = sizes.get(platform, (1080, 1080))
        
        prompt = f"{topic} social media post, modern design"
        
        return self.generate(
            prompt=prompt,
            width=width,
            height=height
        )


def main():
    """Test del agente"""
    agent = ImageAgent()
    
    print("Testing ImageAgent...")
    
    result = agent.generate_for_article(
        topic="Python programming",
        title="Aprende Python"
    )
    
    if result['success']:
        print(f"SUCCESS: {result['filepath']}")
    else:
        print(f"FAILED: {result.get('error')}")


if __name__ == "__main__":
    main()
