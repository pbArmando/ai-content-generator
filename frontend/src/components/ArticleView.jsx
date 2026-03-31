import { useState } from 'react'

function ArticleView({ article, onNewArticle }) {
  const [activeTab, setActiveTab] = useState('article')

  const getQAScoreClass = (score) => {
    if (score >= 80) return 'qa-good'
    if (score >= 60) return 'qa-warning'
    return 'qa-bad'
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <button onClick={onNewArticle} className="btn btn-secondary">
            ← Nuevo Artículo
          </button>
          
          {article.qa_score && (
            <span className={`qa-score ${getQAScoreClass(article.qa_score)}`}>
              QA Score: {article.qa_score}/100
            </span>
          )}
        </div>

        <div className="metadata">
          <div className="metadata-item">
            <span className="metadata-label">Tema</span>
            <span className="metadata-value">{article.topic}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Tono</span>
            <span className="metadata-value">{article.tone}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Palabras</span>
            <span className="metadata-value">{article.word_count || 'N/A'}</span>
          </div>
          {article.security_passed !== undefined && (
            <div className="metadata-item">
              <span className="metadata-label">Seguridad</span>
              <span className="metadata-value" style={{ color: article.security_passed ? '#22c55e' : '#ef4444' }}>
                {article.security_passed ? '✓ Aprobado' : '⚠ Revisado'}
              </span>
            </div>
          )}
        </div>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'article' ? 'active' : ''}`}
          onClick={() => setActiveTab('article')}
        >
          📄 Artículo
        </button>
        <button
          className={`tab ${activeTab === 'social' ? 'active' : ''}`}
          onClick={() => setActiveTab('social')}
        >
          📱 Redes Sociales
        </button>
        <button
          className={`tab ${activeTab === 'prompts' ? 'active' : ''}`}
          onClick={() => setActiveTab('prompts')}
        >
          🖼️ Prompts de Imagen
        </button>
      </div>

      {activeTab === 'article' && (
        <div className="card article-content">
          <h1>{article.title}</h1>
          
          <h2>Introducción</h2>
          <p>{article.introduction}</p>
          
          {article.sections && article.sections.map((section, idx) => (
            <div key={idx}>
              <h2>{section.title}</h2>
              <p>{section.content}</p>
            </div>
          ))}
          
          <h2>Conclusión</h2>
          <p>{article.conclusion}</p>
        </div>
      )}

      {activeTab === 'social' && (
        <div className="social-posts">
          {article.social_posts && Object.entries(article.social_posts).map(([platform, post]) => (
            <div key={platform} className="card social-post">
              <h3>{platform}</h3>
              {post.success ? (
                <div>
                  <p style={{ marginBottom: '10px' }}>{post.content}</p>
                  {post.hashtags && (
                    <p style={{ color: '#2563eb', fontSize: '0.875rem' }}>{post.hashtags}</p>
                  )}
                </div>
              ) : (
                <p style={{ color: '#ef4444' }}>Error: {post.error}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {activeTab === 'prompts' && (
        <div className="card">
          <h3 style={{ marginBottom: '15px' }}>Prompt para Artículo</h3>
          <div className="prompt-box">
            {article.image_prompts?.article || 'No disponible'}
          </div>

          <h3 style={{ margin: '30px 0 15px' }}>Prompts para Redes Sociales</h3>
          <div className="social-posts">
            {article.image_prompts?.social && Object.entries(article.image_prompts.social).map(([platform, prompt]) => (
              <div key={platform} className="card">
                <h4 style={{ marginBottom: '10px', textTransform: 'uppercase' }}>{platform}</h4>
                <div className="prompt-box">{prompt}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ArticleView