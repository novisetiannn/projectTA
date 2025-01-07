import queue

# Inisialisasi antrian suara
speech_queue = queue.Queue()
error_announced = False  # Variabel global untuk melacak apakah error telah diumumkan
error_timestamp = None  # Variabel waktu untuk membatasi pengulangan error