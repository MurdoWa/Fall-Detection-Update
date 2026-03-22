import pyaudio
import numpy as np
from ImageDetection import *
from FileManager import *
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import time
import keyboard

# Audio configuration
CHUNK = 1024
RATE = 16000

# 🔴 Local pause state
paused_local = False


def CheckLocalPause():
    """
    Toggle pause when 'p' is pressed.
    """
    global paused_local

    if keyboard.is_pressed('p'):
        paused_local = not paused_local

        if paused_local:
            print("⏸️ Paused (press 'p' to resume)")
        else:
            print("▶️ Resumed")

        time.sleep(0.5)  # debounce


def Listen(Audiothreshold, device_index=None):
    """
    Listens to audio input until the RMS volume exceeds the threshold.
    Supports pause during listening.
    """
    p = pyaudio.PyAudio()
    stream = None

    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            input_device_index=device_index
        )

        print("Listening...")

        while True:

            # 🔴 LOCAL PAUSE
            CheckLocalPause()
            if paused_local:
                time.sleep(0.2)
                continue

            try:
                data = np.frombuffer(
                    stream.read(CHUNK, exception_on_overflow=False),
                    dtype=np.int16
                )
            except IOError as e:
                print("Audio read error:", e)
                continue

            rms = np.sqrt(np.mean(data.astype(np.float32) ** 2))
            if np.isnan(rms):
                rms = 0

            volume = int(min((rms / 32768) * 100, 100))
            print(volume)

            if volume > Audiothreshold:
                break

    finally:
        if stream is not None:
            stream.stop_stream()
            stream.close()
        p.terminate()
        print("Audio stream closed.")


def main():
    """
    Main function to initialize Firebase, capture images, predict falls,
    and upload results.
    """

    # Firebase still used for uploading results (NOT pausing)
    cred = credentials.Certificate('soc10101-fall-detection-firebase-adminsdk-fbsvc-601713d01f.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Connected to Firebase successfully!")

    threshold = 0.6
    saveLocation = "images/"
    cameraAmount = 2
    predictions = [0] * cameraAmount

    while True:

        # 🔴 LOCAL PAUSE
        CheckLocalPause()
        if paused_local:
            time.sleep(0.2)
            continue

        # 🎤 Listen for trigger sound
        Listen(10)

        # 🔴 Pause again after listening
        CheckLocalPause()
        if paused_local:
            continue

        # 📷 Capture + predict
        for i in range(cameraAmount):

            # Pause-safe loop
            while paused_local:
                CheckLocalPause()
                time.sleep(0.2)

            TakeIMG(saveLocation, "TEMPNAME.png", i)

            imgArray = ProcessImg(saveLocation + "TEMPNAME.png")

            predictions[i] = FallDetect(imgArray, threshold)

            RenameIMG(saveLocation, predictions[i], threshold)

        # 📊 Final decision
        fallPredFinal = MeanResults(predictions)

        timestamp = datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
        fallDetected = bool(fallPredFinal < threshold)

        # ☁️ Upload result
        db.collection("FallEvents").document("events").set({
            "timestamp": timestamp,
            "fall": fallDetected
        }, merge=True)

        print(f"Uploaded to Firebase: {timestamp} -> {fallDetected}")

        if fallDetected:
            print("🚨 Fall Detected! 🚨")
        else:
            print("✅ No Fall Detected.")

        time.sleep(0.5)


if __name__ == "__main__":
    main()
