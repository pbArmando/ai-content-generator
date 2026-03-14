import os
import sys
import time
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Agregar src al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

load_dotenv()

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

from services.cache_service import CacheService


class ResearchAgent:
    def __init__(self, max_sources: int = 5, use_cache: bool = True):
        self.max_sources = max_sources
        self.use_cache = use_cache
        self.cache = CacheService(ttl_hours=24) if use_cache else None
        self.client = None
        self._setup_tavily()

    def _setup_tavily(self):
        if not TAVILY_AVAILABLE:
            raise ImportError("Tavily no está instalado. Ejecuta: pip install tavily")
        
        api_key = os.getenv('TAVILY_API_KEY')
        if not api_key:
            raise ValueError("No se encontró TAVILY_API_KEY en el archivo .env")
        
        self.client = TavilyClient(api_key=api_key)

    def search(self, query: str, include_answer: bool = True) -> Dict[str, Any]:
        if self.use_cache:
            cached_result = self.cache.get(query)
            if cached_result:
                return cached_result
        
        try:
            response = self.client.search(
                query=query,
                max_results=self.max_sources,
                include_answer=include_answer,
                include_raw_content=False,
                include_images=False
            )
            
            result = {
                'query': query,
                'answer': response.get('answer'),
                'results': self._format_results(response.get('results', [])),
                'sources': [r['url'] for r in response.get('results', [])[:self.max_sources]]
            }
            
            if self.use_cache and result['results']:
                self.cache.set(query, result)
            
            return result
            
        except Exception as e:
            return {
                'query': query,
                'answer': None,
                'results': [],
                'sources': [],
                'error': str(e)
            }

    def _format_results(self, results: List[Dict]) -> List[Dict]:
        formatted = []
        for r in results[:self.max_sources]:
            formatted.append({
                'title': r.get('title', ''),
                'url': r.get('url', ''),
                'content': r.get('content', '')[:500],
                'score': r.get('score', 0)
            })
        return formatted

    def research_topic(self, topic: str) -> Dict[str, Any]:
        search_queries = [
            topic,
            f"{topic} 2025 2026",
            f"qué es {topic}",
            f"beneficios de {topic}"
        ]
        
        all_results = {
            'topic': topic,
            'main_results': None,
            'recent_results': None,
            'sources': []
        }
        
        print(f"🔍 Investigando: {topic}")
        
        main_result = self.search(search_queries[0])
        all_results['main_results'] = main_result
        if main_result.get('sources'):
            all_results['sources'].extend(main_result['sources'])
        
        if main_result.get('answer'):
            print(f"   ✅ Respuesta encontrada")
        
        time.sleep(0.5)
        
        recent_result = self.search(search_queries[1])
        if recent_result.get('results'):
            all_results['recent_results'] = recent_result
            for source in recent_result.get('sources', []):
                if source not in all_results['sources']:
                    all_results['sources'].append(source)
            print(f"   ✅ {len(recent_result['results'])} resultados recientes")
        
        all_results['sources'] = all_results['sources'][:self.max_sources]
        
        return all_results

    def format_for_prompt(self, research_data: Dict[str, Any]) -> str:
        if research_data.get('error'):
            return ""
        
        context_parts = []
        
        if research_data.get('answer'):
            context_parts.append(f"RESPUESTA GENERAL:\n{research_data['answer']}\n")
        
        if research_data.get('main_results', {}).get('results'):
            context_parts.append("INFORMACIÓN ACTUALIZADA:")
            for i, r in enumerate(research_data['main_results']['results'][:3], 1):
                context_parts.append(f"\n{i}. {r['title']}")
                context_parts.append(f"   {r['content']}")
                context_parts.append(f"   Fuente: {r['url']}")
        
        if research_data.get('sources'):
            context_parts.append(f"\nFUENTES CONSULTADAS:")
            for src in research_data['sources']:
                context_parts.append(f"- {src}")
        
        return "\n".join(context_parts)
