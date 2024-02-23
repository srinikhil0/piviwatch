import cv2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import tkinter as tk
from tkinter import messagebox
import numpy as np
import os

# Initialize encryption
def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    return cipher.iv, ct_bytes

# Show a simple notification
def show_notification(message):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Notification", message)
    root.destroy()

# Main SecureCam function
def secure_cam(video_path, encryption_key):
    cap = cv2.VideoCapture(video_path)
   
    if not cap.isOpened():
        print(f"Error opening video file {video_path}")
        return

    ret, previous_frame = cap.read()
    previous_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
    
    # Extract video base name and create a directory for encrypted segments
    video_base_name = os.path.splitext(os.path.basename(video_path))[0]
    encrypted_segments_dir = os.path.join(os.path.dirname(video_path), video_base_name)
    if not os.path.exists(encrypted_segments_dir):
        os.makedirs(encrypted_segments_dir)
    
    segment_count = 0  # Counter for encrypted segments

    while cap.isOpened():
        ret, current_frame = cap.read()
        if not ret:
            break
        
        current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        frame_diff = cv2.absdiff(previous_gray, current_gray)
        _, thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)
        motion_detected = np.sum(thresh) > 0  # Simplified motion detection
        
        if motion_detected:
            frame_data_as_bytes = thresh.tobytes()
            iv, encrypted_frame = encrypt_data(frame_data_as_bytes, encryption_key)
            
            # Save the encrypted frame to a file in the new directory
            segment_filename = f"encrypted_segment_{segment_count}.bin"
            segment_path = os.path.join(encrypted_segments_dir, segment_filename)
            with open(segment_path, "wb") as file:
                file.write(iv + encrypted_frame)  # Prepend IV for decryption
            segment_count += 1  # Increment the counter
            
            print(f"Motion detected and frame encrypted, saved as {segment_path}")
        
        previous_gray = current_gray.copy()
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    show_notification("Processing Complete")

# Example usage
encryption_key = b'ThisIs16ByteKey!'  # Ensure this is a 16-byte key
secure_cam('sample.mp4', encryption_key)
