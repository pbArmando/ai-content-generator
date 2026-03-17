"""
Script para generar artículos completos - Versión Optimizada
Usa agentes independientes para menor consumo de tokens
Incluye sistema de QA como security review

Uso:
    python generate_article.py --topic "tu tema" --tone profesional --research
    python generate_article.py --help
"""

import os
import sys
import argparse
import pathlib

# Configurar UTF-8 para emojis en Windows
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from datetime import datetime

# Agregar src al path de manera robusta
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR / 'src'))

from agents.orchestrator import OrchestratorAgent
from agents.research_agent import ResearchAgent
from agents.qa_agent import ContentQAAgent, ContentSecurityAgent
from agents.image_agent import ImageAgent
from agents.social_media_agent import SocialMediaAgent
from services.cache_service import CacheService


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    print("=" * 70)
    print("GENERADOR DE ARTICULOS OPTIMIZADO")
    print("   [Agentes independientes - Menor consumo de tokens]")
    print("=" * 70)
    print()


def format_article_markdown(article):
    markdown = f"""# {article['title']}

**Tema:** {article['topic']}  
**Tono:** {article['tone']}  
**Palabras:** ~{article['word_count']}  
**Fecha:** {datetime.now().strftime('%Y-%m-%d')}

---

## Introduccion

{article['introduction']}

---

"""

    if article.get('sections'):
        for section in article['sections']:
            markdown += f"## {section['title']}\n\n{section['content']}\n\n---\n\n"

    markdown += f"""## Conclusion

{article['conclusion']}

---

*Articulo generado automaticamente con IA*
"""
    return markdown


def save_article(article, format='markdown'):
    safe_topic = "".join(c for c in article['topic'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_topic = safe_topic.replace(' ', '_')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == 'markdown':
        filename = f"outputs/article_{safe_topic}_{timestamp}.md"
        content = format_article_markdown(article)
    else:
        filename = f"outputs/article_{safe_topic}_{timestamp}.txt"
        content = f"""TITULO: {article['title']}
TEMA: {article['topic']}
TONO: {article['tone']}
FECHA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{"="*70}

INTRODUCCION:
{article['introduction']}

{"="*70}

CONCLUSION:
{article['conclusion']}

{"="*70}
*Articulo generado automaticamente con IA*
"""
    
    os.makedirs("outputs", exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename


def generate_article(topic, tone="profesional", use_research=False):
    """Genera un articulo - sin interaccion"""
    
    print(f"[INFO] Generando articulo sobre: {topic}")
    print(f"[INFO] Tono: {tone}")
    print(f"[INFO] Investigacion: {'si' if use_research else 'no'}")
    
    try:
        research_agent = ResearchAgent()
        orchestrator = OrchestratorAgent()
    except Exception as e:
        print(f"[ERROR] Error al inicializar: {e}")
        return None
    
    research_context = ""
    if use_research:
        print("[INFO] Investigando tema...")
        try:
            research_data = research_agent.research_topic(topic)
            research_context = research_agent.format_for_prompt(research_data)
            print(f"[INFO] {len(research_data.get('sources', []))} fuentes encontradas")
        except Exception as e:
            print(f"[WARN] Error en investigacion: {e}")
    
    print("[INFO] Generando articulo...")
    article = orchestrator.generate_article(topic, tone, research_context)
    
    if "error" in article:
        print(f"[ERROR] {article['error']}")
        return None
    
    # QA
    print("[INFO] Verificando calidad...")
    try:
        qa_agent = ContentQAAgent()
        qa_report = qa_agent.analyze_article(article)
        print(f"[INFO] Puntuacion de calidad: {qa_report.score}/100")
        
        if qa_report.findings:
            for f in qa_report.findings[:3]:
                print(f"[WARN] {f['severity'].upper()}: {f['message']}")
        
        security_agent = ContentSecurityAgent()
        security_report = security_agent.scan_article(article)
        
        if not security_report.passed:
            print(f"[ALERT] Problemas de seguridad encontrados")
    except Exception as e:
        print(f"[WARN] QA no disponible: {e}")
    
    # Generar imagen
    print("[INFO] Generando imagen...")
    try:
        image_agent = ImageAgent()
        image_result = image_agent.generate_for_article(
            topic=topic,
            title=article.get('title', topic)
        )
        
        if image_result['success']:
            print(f"[INFO] Imagen generada: {image_result['filepath']}")
            article['image'] = image_result
        else:
            print(f"[WARN] No se pudo generar imagen: {image_result.get('error')}")
    except Exception as e:
        print(f"[WARN] ImageAgent no disponible: {e}")
    
    return article


def main():
    parser = argparse.ArgumentParser(description='Generador de articulos con IA')
    parser.add_argument('--topic', '-t', type=str, help='Tema del articulo')
    parser.add_argument('--tone', type=str, default='profesional', 
                       choices=['profesional', 'casual', 'tecnico'],
                       help='Tono del articulo')
    parser.add_argument('--research', '-r', action='store_true',
                       help='Habilitar busqueda web')
    parser.add_argument('--output', '-o', type=str, default='markdown',
                       choices=['markdown', 'txt', 'both'],
                       help='Formato de salida')
    
    args = parser.parse_args()
    
    if not args.topic:
        # Modo interactivo
        clear_screen()
        print_header()
        
        print("Tema del articulo: ", end="")
        topic = input().strip()
        if not topic:
            print("Debes ingresar un tema")
            return
        
        print("Deseas busqueda web? (s/n): ", end="")
        use_research = input().strip().lower() == 's'
        
        print("Tono (1=profesional, 2=casual, 3=tecnico): ", end="")
        tone_choice = input().strip()
        tones = {"1": "profesional", "2": "casual", "3": "tecnico"}
        tone = tones.get(tone_choice, "profesional")
    else:
        topic = args.topic
        use_research = args.research
        tone = args.tone
    
    article = generate_article(topic, tone, use_research)
    
    if article:
        print(f"\n[SUCCESS] Articulo generado: {article['title']}")
        
        if args.output in ['markdown', 'both']:
            filename_md = save_article(article, format='markdown')
            print(f"[SUCCESS] Guardado: {filename_md}")
        
        if args.output in ['txt', 'both']:
            filename_txt = save_article(article, format='txt')
            print(f"[SUCCESS] Guardado: {filename_txt}")
        
        # Generar posts para redes sociales
        print("\n[INFO] Generando posts para redes sociales...")
        try:
            social_agent = SocialMediaAgent()
            social_results = social_agent.generate_all(article)
            
            # Guardar posts
            os.makedirs("outputs", exist_ok=True)
            social_file = f"outputs/social_posts_{article['topic'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(social_file, 'w', encoding='utf-8') as f:
                f.write(f"Posts para redes sociales - Tema: {article['topic']}\n")
                f.write("="*50 + "\n\n")
                
                for platform, result in social_results.items():
                    f.write(f"--- {platform.upper()} ---\n")
                    if result['success']:
                        f.write(result['content'] + "\n\n")
                    else:
                        f.write(f"Error: {result.get('error')}\n\n")
            
            print(f"[SUCCESS] Posts guardados: {social_file}")
            
            # Mostrar posts
            print("\n" + "="*50)
            print("POSTS PARA REDES SOCIALES")
            print("="*50)
            for platform, result in social_results.items():
                print(f"\n[{platform.upper()}]")
                if result['success']:
                    print(result['content'][:300] + "...")
                else:
                    print(f"Error: {result.get('error')}")
            
        except Exception as e:
            print(f"[WARN] No se pudieron generar posts sociales: {e}")
        
        print(format_article_markdown(article))
    else:
        print("[ERROR] No se pudo generar el articulo")
        sys.exit(1)


if __name__ == "__main__":
    main()
