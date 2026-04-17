import pyaudio
import numpy as np
from ImageDetection import *
from FileManager import *
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import time
import os
import scipy.signal

# Audio configuration
CHUNK = 1024
RATE = 16000

# Begins Listening Function
#Audio Threshold is the average
#Peak threshold is the peak
def Listen(Audiothreshold=110, PeakThreshold=2000, device_index=None, chunks_to_average=10):

    p = pyaudio.PyAudio()
    stream = None
    rms_values = []

    # Low-pass filter helper
    def lowpass_filter(signal, cutoff=300, fs=RATE, order=4):
        b, a = scipy.signal.butter(order, cutoff / (0.5 * fs), btype='low')
        return scipy.signal.lfilter(b, a, signal)

    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            input_device_index=device_index
        )

        print("Listening for impact...")

        while True:
            try:
                data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
            except IOError as e:
                print("Audio read error:", e)
                continue

            # Low-pass filter for soft impact emphasis
            filtered = lowpass_filter(data)

            # RMS and peak
            rms = np.sqrt(np.mean(filtered.astype(np.float32) ** 2))
            peak = np.max(np.abs(filtered))

            # Rolling RMS average
            rms_values.append(rms)
            if len(rms_values) > chunks_to_average:
                rms_values.pop(0)
            avg_rms = np.mean(rms_values)

            print(f"RMS: {avg_rms:.1f}, Peak: {peak}")

            # Trigger condition
            if avg_rms > Audiothreshold or peak > PeakThreshold:
                print("Impact detected!")
                return avg_rms, peak

    finally:
        if stream is not None:
            stream.stop_stream()
            stream.close()
        p.terminate()
        print("Audio stream closed.")


def main():

    # Ask user for number of cameras
    while True:
        try:
            cameraAmount = int(input("Enter number of cameras to use: "))
            if cameraAmount > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")

    # Firebase initialization
    cred = credentials.Certificate('soc10101-fall-detection-firebase-adminsdk-fbsvc-601713d01f.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Connected to Firebase successfully!")

    # Ask user for collection name
    collection_name = input("Enter the Firestore collection name to push events to: ").strip()
    if not collection_name:
        collection_name = "FallEvents"
        print(f"No name entered, defaulting to '{collection_name}'.")

    # Ask user whether to save or delete images after processing
    while True:
        save_choice = input("Save images after processing? (y/n): ").strip().lower()
        if save_choice in ("y", "n"):
            saveImages = save_choice == "y"
            break
        else:
            print("Please enter 'y' or 'n'.")

    threshold = 0.6
    saveLocation = "images/"
    predictions = [0] * cameraAmount

    while True:

        # Listen for trigger sound and get RMS + Peak
        rms_value, peak_value = Listen()

        # Capture + predict
        for i in range(cameraAmount):

            TakeIMG(saveLocation, "TEMPNAME.png", i)

            imgArray = ProcessImg(saveLocation + "TEMPNAME.png")

            predictions[i] = FallDetect(imgArray, threshold)

            renamed_file = RenameIMG(saveLocation, predictions[i], threshold)

            if not saveImages:
                filepath = os.path.join(saveLocation, renamed_file)
                if os.path.exists(filepath):
                    os.remove(filepath)

        # Final decision
        fallPredFinal = MeanResults(predictions)

        timestamp = datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
        fallDetected = bool(fallPredFinal < threshold)

        # Upload result to Firebase
        db.collection(collection_name).document(timestamp).set({
            "timestamp": timestamp,
            "fall": fallDetected,
            "prediction_score": float(fallPredFinal),
            "rms": float(rms_value)
        })

        print(f"Uploaded to Firebase: {timestamp} -> {fallDetected} (score={fallPredFinal}, RMS={rms_value:.1f}, Peak={peak_value})")

        if fallDetected:
            print("Fall Detected!")
        else:
            print("No Fall Detected.")

        time.sleep(0.5)


if __name__ == "__main__":
    main()
