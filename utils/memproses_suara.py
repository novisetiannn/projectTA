import playsound
from gtts import gTTS
import os
from utils.inisialisasi_antrian_suara import speech_queue

# Fungsi untuk memproses suara dari antrian menggunakan gTTS dan playsound
def speak_from_queue(speech_queue):
    while True:
        text = speech_queue.get()
        if text:  # Jika ada teks dalam antrian
            try:
                # Buat file suara sementara dari teks
                tts = gTTS(text=text, lang='id')
                tts.save("temp_speech.mp3")

                # Putar file suara
                playsound("temp_speech.mp3")

            except Exception as e:
                print(f"Error playing sound: {e}")
            finally:
                # Hapus file sementara setelah diputar, pastikan file ada sebelum menghapus
                if os.path.exists("temp_speech.mp3"):
                    os.remove("temp_speech.mp3")
                
                speech_queue.task_done()  # Menandakan tugas selesai