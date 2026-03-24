import os
import sys
from typing import Dict, Any, Tuple
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class TextOverlayAgent:
    """
    Agente que agrega texto a imágenes para redes sociales.
    Sin costo de API - usa Pillow para procesamiento local.
    """
    
    # Configuración por plataforma
    PLATFORM_CONFIG = {
        'instagram': {
            'text_position': 'bottom',  # Abajo
            'font_size_ratio': 0.06,    # 6% del ancho de imagen
            'padding': 0.05,            # 5% de padding
            'max_lines': 3,
            'text_color': (255, 255, 255),  # Blanco
            'shadow': True
        },
        'twitter': {
            'text_position': 'bottom',
            'font_size_ratio': 0.05,
            'padding': 0.04,
            'max_lines': 2,
            'text_color': (255, 255, 255),
            'shadow': True
        },
        'facebook': {
            'text_position': 'bottom',
            'font_size_ratio': 0.05,
            'padding': 0.04,
            'max_lines': 2,
            'text_color': (255, 255, 255),
            'shadow': True
        },
        'linkedin': {
            'text_position': 'bottom',
            'font_size_ratio': 0.05,
            'padding': 0.04,
            'max_lines': 2,
            'text_color': (255, 255, 255),
            'shadow': True
        }
    }
    
    def __init__(self, output_dir: str = "outputs/images_with_text"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not PIL_AVAILABLE:
            raise ImportError("Pillow no está instalado. Ejecuta: pip install Pillow")
    
    def add_text_to_image(self, image_path: str, text: str, platform: str = "instagram") -> Dict[str, Any]:
        """
        Agrega texto a una imagen para redes sociales.
        
        Args:
            image_path: Ruta de la imagen original
            text: Texto a agregar
            platform: Plataforma de redes sociales
            
        Returns:
            dict con 'success', 'filepath', 'original_image'
        """
        if not PIL_AVAILABLE:
            return {'success': False, 'error': 'Pillow no instalado'}
        
        try:
            # Cargar imagen
            img = Image.open(image_path).convert('RGBA')
            width, height = img.size
            
            # Crear capa de texto
            txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_layer)
            
            # Obtener configuración de la plataforma
            config = self.PLATFORM_CONFIG.get(platform, self.PLATFORM_CONFIG['instagram'])
            
            # Calcular tamaño de fuente
            font_size = int(width * config['font_size_ratio'])
            
            # Intentar cargar fuente (si no existe, usar defecto)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # Preparar texto (líneas)
            lines = self._wrap_text(text, font, draw, width * 0.9, config['max_lines'])
            
            # Calcular posición
            line_height = font_size * 1.3
            total_text_height = len(lines) * line_height
            padding = int(width * config['padding'])
            
            # Posición Y según configuración
            if config['text_position'] == 'bottom':
                y_start = height - total_text_height - padding
            else:  # top
                y_start = padding
            
            x = width / 2  # Centrado horizontalmente
            
            # Dibujar cada línea
            for i, line in enumerate(lines):
                y = y_start + (i * line_height)
                
                # Sombra si está habilitada
                if config['shadow']:
                    shadow_offset = int(font_size * 0.05)
                    draw.text((x + shadow_offset, y + shadow_offset), line, 
                              font=font, fill=(0, 0, 0, 180), anchor='mm')
                
                # Texto principal
                draw.text((x, y), line, font=font, 
                          fill=config['text_color'] + (255,), anchor='mm')
            
            # Combinar imagen con capa de texto
            final_img = Image.alpha_composite(img, txt_layer)
            
            # Convertir a RGB para guardar como PNG/JPG
            final_img = final_img.convert('RGB')
            
            # Generar nombre de archivo
            original_name = Path(image_path).stem
            new_name = f"{original_name}_{platform}_text.png"
            output_path = self.output_dir / new_name
            
            # Guardar
            final_img.save(output_path, 'PNG')
            
            return {
                'success': True,
                'filepath': str(output_path),
                'original_image': image_path,
                'platform': platform,
                'text': text,
                'lines': lines
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original_image': image_path
            }
    
    def _wrap_text(self, text: str, font, draw, max_width: int, max_lines: int) -> list:
        """
        Envuelve el texto en líneas basing en el ancho máximo.
        """
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width > max_width and len(current_line) > 1:
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]
                
                if len(lines) >= max_lines:
                    # Truncar última línea con "..."
                    if lines:
                        last_bbox = draw.textbbox((0, 0), lines[-1], font=font)
                        max_chars = len(lines[-1]) - 3
                        lines[-1] = lines[-1][:max_chars] + '...'
                    break
        
        if current_line and len(lines) < max_lines:
            lines.append(' '.join(current_line))
        
        return lines[:max_lines]
    
    def generate_social_text(self, post_content: str, platform: str = "instagram") -> str:
        """
        Genera texto optimizado para agregar a imágenes de redes sociales.
        Extrae lo más importante del post.
        """
        if not post_content:
            return ""
        
        # Limpiar el texto
        text = post_content.strip()
        
        # Límites por plataforma
        limits = {
            'instagram': 125,
            'twitter': 70,
            'facebook': 100,
            'linkedin': 100
        }
        
        limit = limits.get(platform, 125)
        
        # Si es muy largo, truncar intelligently
        if len(text) > limit:
            # Buscar último espacio antes del límite
            truncated = text[:limit]
            last_space = truncated.rfind(' ')
            if last_space > limit * 0.7:  # Si hay espacio razonable
                truncated = truncated[:last_space]
            text = truncated + "..."
        
        return text


def main():
    """Test del agente"""
    if not PIL_AVAILABLE:
        print("ERROR: Pillow no está instalado")
        print("Ejecuta: pip install Pillow")
        return
    
    agent = TextOverlayAgent()
    
    print("Testing TextOverlayAgent...")
    
    # Test con imagen de ejemplo
    test_texts = {
        'instagram': "Protege a tu familia con un seguro de vida",
        'twitter': "Seguro de vida: protección para los tuyos",
        'linkedin': "La importancia de planificar tu futuro financiero"
    }
    
    print("\nTextos generados:")
    for platform, text in test_texts.items():
        generated = agent.generate_social_text(text, platform)
        print(f"  {platform}: {generated}")


if __name__ == "__main__":
    main()
