from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import cv2
import os

def decrypt_data(encrypted_data, key):
    iv = encrypted_data[:16]  # Assuming the IV is the first 16 bytes
    encrypted_data = encrypted_data[16:]
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    return data

def reconstruct_video(decrypted_frames_dir, output_video_path, frame_size, fps=20.0):
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, frame_size)
    
    for frame_file in sorted(os.listdir(decrypted_frames_dir)):
        frame_path = os.path.join(decrypted_frames_dir, frame_file)
        # Assuming the frames are stored as images
        frame = cv2.imread(frame_path)
        if frame is not None:
            out.write(frame)
    out.release()

key = b'\x0fT\xaf\xe5Z\xe4\x88\xe1\\U\t\xc8\x00\xc90\x98>ex\x9b\x882\xf2\xee\x9b\x1c$;0\xef\x1bA'  # Use the same key used for encryption

# Decrypt each file and save as an image (or directly in memory)
decrypted_frames_dir = 'output/'
encrypted_files_dir = 'sample/'
for encrypted_file in sorted(os.listdir(encrypted_files_dir)):
    with open(os.path.join(encrypted_files_dir, encrypted_file), 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = decrypt_data(encrypted_data, key)
    frame_path = os.path.join(decrypted_frames_dir, encrypted_file.replace('.bin', '.jpg'))
    with open(frame_path, 'wb') as frame_file:
        frame_file.write(decrypted_data)

# Reconstruct the video from decrypted frames
output_video_path = 'sample.mp4'
frame_size = (1920, 1080)  # Set to the size of your original frames
reconstruct_video(decrypted_frames_dir, output_video_path, frame_size)
