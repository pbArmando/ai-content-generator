"""
ArticleService - Lógica de negocio para artículos
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import sys
import pathlib

# Agregar src al path
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

# Importar agentes
from agents.orchestrator import OrchestratorAgent
from agents.research_agent import ResearchAgent
from agents.qa_agent import ContentQAAgent, ContentSecurityAgent
from agents.social_media_agent import SocialMediaAgent
from agents.prompt_agent import PromptAgent


class ArticleService:
    def __init__(self):
        self.articles: Dict[str, Dict] = {}
    
    def generate_article(self, topic: str, tone: str = "profesional", use_research: bool = False) -> Dict[str, Any]:
        """Genera un artículo completo"""
        
        article_id = str(uuid.uuid4())
        
        # Inicializar agentes
        research_agent = ResearchAgent()
        orchestrator = OrchestratorAgent()
        
        # Investigación web si se solicita
        research_context = ""
        sources = []
        if use_research:
            try:
                research_data = research_agent.research_topic(topic)
                research_context = research_agent.format_for_prompt(research_data)
                sources = research_data.get('sources', [])
            except Exception as e:
                print(f"Error en investigación: {e}")
        
        # Generar artículo
        article = orchestrator.generate_article(topic, tone, research_context)
        
        if "error" in article:
            return {"error": article["error"]}
        
        # QA
        try:
            qa_agent = ContentQAAgent()
            qa_report = qa_agent.analyze_article(article)
            article['qa_score'] = qa_report.score
            article['qa_findings'] = qa_report.findings
            
            security_agent = ContentSecurityAgent()
            security_report = security_agent.scan_article(article)
            article['security_passed'] = security_report.passed
        except Exception as e:
            print(f"Error en QA: {e}")
        
        # Generar prompts de imagen
        try:
            prompt_agent = PromptAgent()
            article_prompt = prompt_agent.generate_article_prompt(article)
            social_prompts = {}
            
            for platform in ['instagram', 'twitter', 'facebook', 'linkedin']:
                social_prompts[platform] = prompt_agent.generate_social_prompt(article, platform)
            
            article['image_prompts'] = {
                'article': article_prompt,
                'social': social_prompts
            }
        except Exception as e:
            print(f"Error en prompts: {e}")
        
        # Generar posts sociales
        try:
            social_agent = SocialMediaAgent()
            social_posts = social_agent.generate_all(article)
            article['social_posts'] = social_posts
        except Exception as e:
            print(f"Error en social posts: {e}")
        
        # Guardar artículo
        article['id'] = article_id
        article['created_at'] = datetime.now().isoformat()
        article['topic'] = topic
        article['tone'] = tone
        article['sources'] = sources
        
        self.articles[article_id] = article
        
        return article
    
    def get_article(self, article_id: str) -> Optional[Dict]:
        """Obtiene un artículo por ID"""
        return self.articles.get(article_id)
    
    def list_articles(self) -> List[Dict]:
        """Lista todos los artículos"""
        return [
            {
                'id': aid,
                'title': a.get('title'),
                'topic': a.get('topic'),
                'tone': a.get('tone'),
                'created_at': a.get('created_at')
            }
            for aid, a in self.articles.items()
        ]
    
    def generate_social_posts(self, topic: str, tone: str = "profesional") -> Dict:
        """Genera solo posts sociales"""
        article = self.generate_article(topic, tone, use_research=False)
        return article.get('social_posts', {})
    
    def get_image_prompts(self, article_id: str) -> Optional[Dict]:
        """Obtiene los prompts de imagen"""
        article = self.get_article(article_id)
        if article:
            return article.get('image_prompts')
        return None