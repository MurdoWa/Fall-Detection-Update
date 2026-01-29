import pyaudio
from ImageDetection import *
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

CHUNK = 1024
RATE = 44100


def listen(threshold):
    p = pyaudio.PyAudio()
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
        if volume > threshold:
            break

def main():

    # Initialize Firebase with service account
    cred = credentials.Certificate('soc10101-fall-detection-firebase-adminsdk-fbsvc-5c93a456e9.json')
    firebase_admin.initialize_app(cred)
    # Get Firestore client
    db = firestore.client()
    print("Connected to Firebase successfully!")


    imageAmount = 1
    saveLocation ="images/"
    fileName = "captured_image"
    fallBool = False

    while True:
        #imageAmount = findNextFile(saveLocation)


        listen(10)
        TakeIMG(saveLocation, "TEMPNAME.png")
        img_array = ProcessImg(saveLocation+"TEMPNAME.png")

        now = datetime.now()
        dt_string = now.strftime("%d_%m_%Y-%H_%M_%S")

        db.collection('ReceivedData').document('Laptop Testing').update({
            dt_string: fallBool,
        })

        RenameIMG(saveLocation, fallBool)



if __name__ == "__main__":
    main()
