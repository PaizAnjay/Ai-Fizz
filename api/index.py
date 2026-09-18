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


@app.route("/", defaults={"req_path": ""}, methods=["GET", "POST"])
