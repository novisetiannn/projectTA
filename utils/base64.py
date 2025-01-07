import base64

# fungsi untuk Mengonversi gambar ke format Base64.
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')