import cv2
import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

def encrypt_data(data, key):
    # Ensure the key is of correct size (AES-256 requires a 32-byte key)
    assert len(key) == 32, "Key must be 32 bytes long"
    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return iv + encrypted_data  # Prepend IV to encrypted data for decryption

key = os.urandom(32)  # In practice, use a more secure way to generate/store the key
print(key)


# Load the video
video_path = 'sample.mp4'
video_name = os.path.splitext(os.path.basename(video_path))[0]
cap = cv2.VideoCapture(video_path)

# Create a new directory named after the video
output_dir = os.path.join(os.path.dirname(video_path), video_name)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

ret, frame1 = cap.read()
ret, frame2 = cap.read()

def save_encrypted_data(encrypted_data, file_path):
    with open(file_path, 'wb') as file:
        file.write(encrypted_data)

frame_counter = 0
while cap.isOpened():
    ret, frame2 = cap.read()
    if not ret:
        break

    encrypted_frame = frame1.copy()  # Assume initial frame as base for encryption visualization

    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 500:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        frame_bytes = cv2.imencode('.jpg', frame1[y:y+h, x:x+w])[1].tobytes()
        encrypted_bytes = encrypt_data(frame_bytes, key)
        encrypted_file_path = os.path.join(output_dir, f"encrypted_frame_{frame_counter}.bin")
        save_encrypted_data(encrypted_bytes, encrypted_file_path)
        frame_counter += 1
        cv2.rectangle(encrypted_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imshow('Encrypted Frame', encrypted_frame)
    if cv2.waitKey(40) == 27:
        break

    frame1 = frame2

cap.release()
cv2.destroyAllWindows()
