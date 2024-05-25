import io
import speech_recognition as sr
from openai import OpenAI

model = "whisper-1"
api_key = "your-openai-api-key"
client = OpenAI(api_key=api_key)


def capture_audio_from_mic():
    """Capture audio from the microphone and return the audio data."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please say something...")
        audio = recognizer.listen(source)
    
    # Convert the audio data to a bytes-like object
    audio_data = io.BytesIO(audio.get_wav_data())
    return audio_data

def transcribe_audio(audio_data):

    # Convert .wav file into speech_recognition's AudioFile format or whatever idrk
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_data) as source:
        audio = recognizer.record(source)
    wav_data = io.BytesIO(audio.get_wav_data())
    wav_data.name = "SpeechRecognition_audio.wav"

    transcript = client.audio.translations.create(model=model, file=wav_data)

    result: str = transcript.text
    print(result)
    return result
