import cv2

# Buka kamera default (index 0)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Camera is not accessible.")
else:
    print("Camera is accessible.")

    while True:
        # Baca frame dari kamera
        ret, frame = cap.read()

        if not ret:
            print("Failed to capture frame.")
            break

        # Tampilkan frame
        cv2.imshow('Camera', frame)

        # Tekan 'q' untuk keluar
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Melepaskan sumber daya kamera
    cap.release()
    cv2.destroyAllWindows()