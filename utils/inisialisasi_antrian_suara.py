import queue
import pyttsx3
import threading
import time

# Inisialisasi antrian suara
speech_queue = queue.Queue()
error_announced = False  # Variabel global untuk melacak apakah error telah diumumkan
error_timestamp = None  # Variabel waktu untuk membatasi pengulangan error

# Inisialisasi engine pyttsx3
engine = pyttsx3.init()

# Sesuaikan kecepatan dan volume suara
engine.setProperty('rate', 150)  # Kecepatan bicara
engine.setProperty('volume', 0.9)  # Volume suara (0.0 - 1.0)

def process_speech_queue():
    """Proses antrian untuk mengucapkan teks."""
    while True:
        if not speech_queue.empty():
            text = speech_queue.get()
            try:
                # Proses teks menjadi suara
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"Error pada TTS: {e}")
        time.sleep(0.1)  # Tunggu sejenak sebelum memeriksa antrian lagi

# Jalankan thread untuk memproses antrian suara
speech_thread = threading.Thread(target=process_speech_queue, daemon=True)
speech_thread.start()
