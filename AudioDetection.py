import pyaudio
from ImageDetection import *
from FileManager import *
import firebase_admin
from firebase_admin import credentials, firestore

#must be changed for Pi
CHUNK = 1024
RATE = 16000

def listen(Audiothreshold):
    #setting our audio stream to p
    p = pyaudio.PyAudio()

    #starting listening
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Listening...")

    while True:
        data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)

        # RMS calculation
        rms = np.sqrt(np.mean(data.astype(np.float32) ** 2))

        if np.isnan(rms):
            rms = 0  # fallback

        # convert to 0–100 volume scale
        volume = int(min((rms / 32768) * 100, 100))
        print(volume)
        if volume > Audiothreshold:
            break

def main():

    # Initialize Firebase with service account
    cred = credentials.Certificate('soc10101-fall-detection-firebase-adminsdk-fbsvc-5c93a456e9.json')
    firebase_admin.initialize_app(cred)
    # Get Firestore client
    db = firestore.client()
    print("Connected to Firebase successfully!")

    #Threshold to detect fall, below 0.6 = fall
    threshold = 0.6
    #filepath to save images
    saveLocation ="images/"
    #amount of cameras in use
    cameraAmount = 1
    #used to store prediction values
    predictions = [0] * cameraAmount

    while True:
        #begins listening
        listen(1)
        i = 0
        #loops to detect falls
        while (i < cameraAmount):
            #takes image
            TakeIMG(saveLocation, "TEMPNAME.png", i)
            #Sets image size
            img_array = ProcessImg(saveLocation + "TEMPNAME.png")
            #predicts fall
            predictions[i] = FallDetect(img_array, threshold)
            #renams image to reflect the fall,
            RenameIMG(saveLocation, predictions[i], threshold)

            i += 1

        #gets mean value based on prediction values
        FallPredFinal = MeanResults(predictions)

        print("Mean prediction:", FallPredFinal)

        #prints fall
        if FallPredFinal < threshold:
            print("Prediction: 🚨 Fall Detected! 🚨")
        else:
            print("Prediction: ✅ No Fall Detected.")




if __name__ == "__main__":
    main()
