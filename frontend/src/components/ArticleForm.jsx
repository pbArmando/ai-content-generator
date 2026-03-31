import { useState } from 'react'

function ArticleForm({ onSubmit, error }) {
  const [topic, setTopic] = useState('')
  const [tone, setTone] = useState('profesional')
  const [useResearch, setUseResearch] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!topic.trim()) return
    onSubmit(topic, tone, useResearch)
  }

  return (
    <div className="card">
      <h2 style={{ marginBottom: '20px' }}>Nueva Generación</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="topic">Tema del artículo</label>
          <input
            type="text"
            id="topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Ej: La importancia de la detección temprana del autismo"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="tone">Tono del contenido</label>
          <select
            id="tone"
            value={tone}
            onChange={(e) => setTone(e.target.value)}
          >
            <option value="profesional">Profesional</option>
            <option value="casual">Casual / Divertido</option>
            <option value="técnico">Técnico</option>
          </select>
        </div>

        <div className="form-group">
          <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={useResearch}
              onChange={(e) => setUseResearch(e.target.checked)}
              style={{ width: 'auto' }}
            />
            <span>Habilitar investigación web (más preciso)</span>
          </label>
        </div>

        {error && (
          <div className="error" style={{ marginBottom: '20px' }}>
            {error}
          </div>
        )}

        <button type="submit" className="btn btn-primary" disabled={!topic.trim()}>
          Generar Contenido
        </button>
      </form>
    </div>
  )
}

export default ArticleForm