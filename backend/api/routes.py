"""
Routes - Endpoints de la API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sys
import pathlib

# Agregar paths
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent
BACKEND_ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))
sys.path.insert(0, str(BACKEND_ROOT / 'services'))

from article_service import ArticleService

router = APIRouter()
article_service = ArticleService()


# Modelos de request
class ArticleRequest(BaseModel):
    topic: str
    tone: str = "profesional"
    use_research: bool = False


class SocialPostRequest(BaseModel):
    article_content: str
    platform: str


# Endpoints
@router.post("/generate-article")
async def generate_article(request: ArticleRequest):
    """Genera un artículo completo"""
    try:
        result = article_service.generate_article(
            topic=request.topic,
            tone=request.tone,
            use_research=request.use_research
        )
        return result
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/article/{article_id}")
async def get_article(article_id: str):
    """Obtiene un artículo por ID"""
    article = article_service.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    return article


@router.get("/articles")
async def list_articles():
    """Lista todos los artículos"""
    return article_service.list_articles()


@router.post("/generate-social-posts")
async def generate_social_posts(request: ArticleRequest):
    """Genera posts para redes sociales"""
    try:
        result = article_service.generate_social_posts(
            topic=request.topic,
            tone=request.tone
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/image-prompts/{article_id}")
async def get_image_prompts(article_id: str):
    """Obtiene los prompts de imagen para un artículo"""
    prompts = article_service.get_image_prompts(article_id)
    if not prompts:
        raise HTTPException(status_code=404, detail="Prompts no encontrados")
    return prompts