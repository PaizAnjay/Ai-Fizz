"""
Server backend untuk ESP32 AI Voice Assistant — versi VERCEL.
- Speech-to-text & jawaban AI : Groq API (gratis, tanpa kartu kredit)
- Text-to-speech              : edge-tts (suara Microsoft Edge, gratis, tanpa API key)

PENTING: Vercel tidak punya ffmpeg bawaan seperti Docker biasa. Kode ini
mengarahkan pydub untuk memakai binary ffmpeg statis yang kamu taruh sendiri
di folder /bin (lihat instruksi di README_VERCEL.md).

Environment variable yang WAJIB diisi di dashboard Vercel:
    GROQ_API_KEY = API key gratis dari https://console.groq.com
"""

import io
import os
import wave
import asyncio
from flask import Flask, request, Response
from groq import Groq
import edge_tts
from pydub import AudioSegment

app = Flask(__name__)
groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

# Arahkan pydub ke ffmpeg statis yang di-bundle di folder /bin (lihat README_VERCEL.md)
_FFMPEG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bin", "ffmpeg")
if os.path.exists(_FFMPEG_PATH):
    AudioSegment.converter = _FFMPEG_PATH

MIC_SAMPLE_RATE = 16000   # harus sama dengan MIC_SAMPLE_RATE di kode ESP32
SPK_SAMPLE_RATE = 16000   # harus sama dengan SPK_SAMPLE_RATE di kode ESP32
TTS_VOICE = "id-ID-GadisNeural"  # suara wanita Bahasa Indonesia. Suara pria: "id-ID-ArdiNeural"


@app.route("/", methods=["GET"])
def health_check():
    """Endpoint kosong untuk cek server hidup."""
    return "OK", 200


async def text_to_speech_pcm(text: str) -> bytes:
    """Ubah teks jadi audio PCM mentah (16-bit mono) sesuai SPK_SAMPLE_RATE."""
    communicate = edge_tts.Communicate(text, TTS_VOICE)
    mp3_bytes = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_bytes += chunk["data"]

    audio = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
    audio = audio.set_frame_rate(SPK_SAMPLE_RATE).set_channels(1).set_sample_width(2)
    return audio.raw_data


@app.route("/chat", methods=["POST"])
def chat():
    raw_pcm = request.data  # audio mentah 16-bit PCM mono dari ESP32

    # bungkus jadi WAV supaya bisa dibaca Groq Whisper
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(MIC_SAMPLE_RATE)
        wf.writeframes(raw_pcm)
    wav_buffer.seek(0)
    wav_buffer.name = "audio.wav"

    # 1. Speech to text (Groq, gratis)
    transcript = groq_client.audio.transcriptions.create(
        model="whisper-large-v3-turbo",
        file=wav_buffer,
    )
    user_text = transcript.text
    print("User bilang:", user_text)

    # 2. Chat AI (Groq, gratis)
    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Jawab singkat, ramah, dan dalam Bahasa Indonesia."},
            {"role": "user", "content": user_text},
        ],
    )
    reply_text = completion.choices[0].message.content
    print("AI jawab:", reply_text)

    # 3. Text to speech (edge-tts, gratis)
    pcm_audio = asyncio.run(text_to_speech_pcm(reply_text))

    return Response(pcm_audio, mimetype="application/octet-stream")


# Vercel mendeteksi variabel bernama `app` ini secara otomatis sebagai WSGI app
