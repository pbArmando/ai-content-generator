"""
Script para generar artículos completos - Versión Optimizada
Usa agentes independientes para menor consumo de tokens
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.orchestrator import OrchestratorAgent
from agents.research_agent import ResearchAgent
from services.cache_service import CacheService


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    print("=" * 70)
    print("📰 GENERADOR DE ARTÍCULOS OPTIMIZADO")
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

## Introducción

{article['introduction']}

---

"""

    if article.get('sections'):
        for section in article['sections']:
            markdown += f"## {section['title']}\n\n{section['content']}\n\n---\n\n"

    markdown += f"""## Conclusión

{article['conclusion']}

---

*Artículo generado automáticamente con IA*
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
        content = f"""TÍTULO: {article['title']}
TEMA: {article['topic']}
TONO: {article['tone']}
FECHA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{"="*70}

INTRODUCCIÓN:
{article['introduction']}

{"="*70}

CONCLUSIÓN:
{article['conclusion']}

{"="*70}
*Artículo generado automáticamente con IA*
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename


def main():
    clear_screen()
    print_header()
    
    try:
        use_research = False
        print("🔧 Inicializando agentes...")
        
        try:
            research_agent = ResearchAgent()
            orchestrator = OrchestratorAgent()
            use_research = True
            print("✅ Agentes listos (con investigación web)")
        except ValueError as e:
            print(f"⚠️ Investigación no disponible: {e}")
            orchestrator = OrchestratorAgent()
            print("✅ Agentes listos (sin investigación)")
        except Exception as e:
            print(f"⚠️ Error: {e}")
            orchestrator = OrchestratorAgent()
            print("✅ Agentes listos (modo básico)")
        
        print()
        
        print("📝 Configuración del artículo:")
        print("-" * 70)
        
        topic = input("Tema del artículo: ").strip()
        if not topic:
            print("❌ Debes ingresar un tema")
            return
        
        if use_research:
            print("\n¿Deseas buscar información actualizada en la web?")
            print("  1. Sí (recomendado)")
            print("  2. No")
            research_choice = input("Elige (1-2) [1]: ").strip() or "1"
            use_research = (research_choice == "1")
        
        print("\nTonos disponibles:")
        print("  1. Profesional")
        print("  2. Casual")
        print("  3. Técnico")
        tone_choice = input("Elige el tono (1-3) [1]: ").strip() or "1"
        
        tones = {"1": "profesional", "2": "casual", "3": "técnico"}
        tone = tones.get(tone_choice, "profesional")
        
        print("\n" + "="*70)
        print(f"🤖 Generando artículo sobre: '{topic}'")
        print(f"📊 Tono: {tone}")
        print("⏳ Procesando...")
        print("="*70)
        
        research_context = ""
        if use_research:
            print("\n🔍 Investigando tema...")
            try:
                research_data = research_agent.research_topic(topic)
                research_context = research_agent.format_for_prompt(research_data)
                print(f"   ✅ {len(research_data.get('sources', []))} fuentes encontradas")
            except Exception as e:
                print(f"   ⚠️ Error en investigación: {e}")
        
        article = orchestrator.generate_article(topic, tone, research_context)
        
        if "error" in article:
            print(f"\n❌ {article['error']}")
            return
        
        print("\n" + "="*70)
        print("✅ ARTÍCULO GENERADO")
        print("="*70)
        print(f"\n📊 Estadísticas:")
        print(f"   - Título: {article['title']}")
        print(f"   - Palabras: ~{article['word_count']}")
        
        if article.get('research_data') and article['research_data'].get('sources'):
            print(f"   - Fuentes: {len(article['research_data']['sources'])}")
        
        filename_md = save_article(article, format='markdown')
        
        print(f"\n💾 Guardado: {filename_md}")
        
        view = input("\n¿Quieres ver el artículo? (s/n): ").strip().lower()
        if view == 's':
            print("\n" + "="*70)
            print(format_article_markdown(article))
            print("="*70)
        
        print("\n✅ ¡Completado!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso cancelado")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
