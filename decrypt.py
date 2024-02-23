from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import cv2
import numpy as np
import os

def is_video_color(video_path):
    """Determine if the video is in color."""
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise ValueError("Could not read frame from video")

    # Calculate the mean absolute difference between color channels
    mean_diff = np.mean(np.abs(frame[:,:,0].astype("int16") - frame[:,:,1].astype("int16"))) + \
                np.mean(np.abs(frame[:,:,1].astype("int16") - frame[:,:,2].astype("int16"))) + \
                np.mean(np.abs(frame[:,:,2].astype("int16") - frame[:,:,0].astype("int16")))

    return mean_diff > 5  # Threshold is arbitrary; adjust based on your needs

def decrypt_data(encrypted_data, key):
    """Decrypt encrypted data using AES."""
    iv = encrypted_data[:16]
    encrypted_content = encrypted_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(encrypted_content), AES.block_size)
    return decrypted_data

def decrypt_segments_to_video(encrypted_segments_dir, output_video_path, decryption_key, frame_shape, is_color, fps=30):
    """Decrypt encrypted segments and compile them into a single video."""
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_video_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    video_writer = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_shape[1], frame_shape[0]))

    for segment_file in sorted(os.listdir(encrypted_segments_dir)):
        segment_path = os.path.join(encrypted_segments_dir, segment_file)
        with open(segment_path, 'rb') as file:
            encrypted_data = file.read()

        decrypted_data = decrypt_data(encrypted_data, decryption_key)

        # if is_color:
        #     frame = np.frombuffer(decrypted_data, dtype=np.uint8).reshape(frame_shape[0], frame_shape[1], 3)
        # else:
        #     frame = np.frombuffer(decrypted_data, dtype=np.uint8).reshape(frame_shape[0], frame_shape[1])

        # Adjusting the reshape for grayscale image
        frame = np.frombuffer(decrypted_data, dtype=np.uint8).reshape(frame_shape[0], frame_shape[1])



        video_writer.write(frame)

    video_writer.release()

# Example usage
video_path = 'sample.mp4'
try:
    color = is_video_color(video_path)
    frame_shape = (480, 640, 3) if color else (480, 640)  # Adjust dimensions as needed
    encrypted_segments_dir = 'sample/'
    output_video_path = 'sample_output/output.mp4'
    decryption_key = b'ThisIs16ByteKey!'
    
    decrypt_segments_to_video(encrypted_segments_dir, output_video_path, decryption_key, frame_shape, color)
    print("Decryption and video compilation completed successfully.")
except ValueError as e:
    print(e)
except Exception as e:
    print(f"An error occurred: {e}")