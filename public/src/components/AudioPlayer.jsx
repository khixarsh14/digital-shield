function AudioPlayer({ audio }) {

  const playAudio = () => {
    const sound = new Audio(audio)
    sound.play()
  }

  return (
    <button className="audio-button" onClick={playAudio}>
      🔊 Listen to explanation
    </button>
  )
}

export default AudioPlayer