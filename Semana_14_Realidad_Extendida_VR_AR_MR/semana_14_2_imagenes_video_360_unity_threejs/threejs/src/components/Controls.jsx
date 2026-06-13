export default function Controls({ mode, onModeChange }) {
  return (
    <div className="controls">
      <button
        className={mode === 'image' ? 'active' : ''}
        onClick={() => onModeChange('image')}
      >
        Imagen 360°
      </button>
      <button
        className={mode === 'video' ? 'active' : ''}
        onClick={() => onModeChange('video')}
      >
        Video 360°
      </button>
    </div>
  )
}
