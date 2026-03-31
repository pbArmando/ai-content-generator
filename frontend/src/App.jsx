import { useState } from 'react'
import axios from 'axios'
import ArticleForm from './components/ArticleForm'
import ArticleView from './components/ArticleView'

function App() {
  const [article, setArticle] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const generateArticle = async (topic, tone, useResearch) => {
    setLoading(true)
    setError(null)
    setArticle(null)

    try {
      const response = await axios.post('/api/generate-article', {
        topic,
        tone,
        use_research: useResearch
      })
      setArticle(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setArticle(null)
    setError(null)
  }

  return (
    <div className="container">
      <header className="header">
        <h1>🤖 AI Content Generator</h1>
        <p>Genera artículos, posts para redes sociales e imágenes con IA</p>
      </header>

      {!article && !loading && (
        <ArticleForm onSubmit={generateArticle} error={error} />
      )}

      {loading && (
        <div className="card">
          <div className="loading">
            <div className="spinner"></div>
            <p>Generando artículo con IA...</p>
            <p style={{ fontSize: '0.875rem', marginTop: '10px' }}>
              Esto puede tomar unos segundos
            </p>
          </div>
        </div>
      )}

      {error && (
        <div className="card">
          <div className="error">
            <strong>Error:</strong> {error}
          </div>
        </div>
      )}

      {article && (
        <ArticleView article={article} onNewArticle={reset} />
      )}
    </div>
  )
}

export default App