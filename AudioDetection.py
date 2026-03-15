import pyaudio
import numpy as np
from ImageDetection import *
from FileManager import *
import firebase_admin
from firebase_admin import credentials, firestore

# Audio configuration
CHUNK = 1024
RATE = 16000

def listen(Audiothreshold, device_index=None):
    """
    Listens to audio input until the RMS volume exceeds the threshold.
    Properly closes the PyAudio stream to avoid device errors.
    """
    p = pyaudio.PyAudio()
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
            try:
                data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
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
        # Properly close the stream and terminate PyAudio
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Audio stream closed.")



def main():
    """
    Main function to initialize Firebase, capture images, predict falls,
    and display results.
    """
    # Initialize Firebase with service account
    cred = credentials.Certificate('soc10101-fall-detection-firebase-adminsdk-fbsvc-5c93a456e9.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Connected to Firebase successfully!")

    # Threshold to detect fall, below 0.6 = fall
    threshold = 0.6

    # Filepath to save images
    saveLocation = "images/"

    # Number of cameras in use
    cameraAmount = 2

    # Used to store prediction values
    predictions = [0] * cameraAmount

    while True:
        # Begin listening
        listen(30)

        i = 0
        while i < cameraAmount:
            # Take image
            TakeIMG(saveLocation, "TEMPNAME.png", i)

            # Set image size
            img_array = ProcessImg(saveLocation + "TEMPNAME.png")

            # Predict fall
            predictions[i] = FallDetect(img_array, threshold)

            # Rename image to reflect prediction
            RenameIMG(saveLocation, predictions[i], threshold)

            i += 1

        # Get mean value based on prediction values
        FallPredFinal = MeanResults(predictions)
        print("Mean prediction:", FallPredFinal)

        # Print fall detection result
        if FallPredFinal < threshold:
            print("Prediction: 🚨 Fall Detected! 🚨")
        else:
            print("Prediction: ✅ No Fall Detected.")

if __name__ == "__main__":
    main()
