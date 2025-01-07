import threading
from utils.memproses_suara import speak_from_queue
from utils.inisialisasi_antrian_suara import speech_queue

# Jalankan thread untuk memutar suara dari antrian
speech_thread = threading.Thread(target=speak_from_queue, args=(speech_queue,))
speech_thread.daemon = True  # Mengatur thread sebagai daemon agar berhenti saat aplikasi berhenti
speech_thread.start()