import speech_recognition as sr
import os
from pydub import AudioSegment
from smolagents import tool


@tool
def transcribe_audio(mp3_path: str) -> str:
  """
  Transcribes text from an MP3 audio file using speech recognition.
  Args:
    mp3_path (str): Path to the MP3 file to be transcribed.
  Returns:
    str: The transcribed text from the audio file.
  Raises:
    FileNotFoundError: If the MP3 file does not exist at the specified path.
    ValueError: If the file is not a valid MP3 file or audio cannot be processed.
    Exception: For other unexpected errors during transcription.
  Example:
    >>> text = transcribe_audio("sample.mp3")
    >>> print(text)
    "Hello, this is a sample audio."
  """
  # Check if file exists
  if not os.path.exists(mp3_path):
    raise FileNotFoundError(f"The file {mp3_path} does not exist.")

  # Initialize recognizer
  recognizer = sr.Recognizer()

  try:
    # Convert MP3 to WAV
    audio = AudioSegment.from_mp3(mp3_path)
    wav_path = mp3_path.replace(".mp3", ".wav")
    audio.export(wav_path, format="wav")

    # Load audio file
    with sr.AudioFile(wav_path) as source:
      # Adjust for ambient noise
      recognizer.adjust_for_ambient_noise(source)
      # Record the audio
      audio_data = recognizer.record(source)

    # Clean up temporary WAV file
    os.remove(wav_path)

    # Perform speech recognition
    text = recognizer.recognize_google(audio_data)
    return text

  except sr.UnknownValueError:
    raise ValueError("Could not understand the audio.")
  except sr.RequestError as e:
    raise ValueError(f"Could not process audio; {e}")
  except Exception as e:
    raise Exception(f"An error occurred during transcription: {e}")