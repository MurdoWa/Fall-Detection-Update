from cv2 import VideoCapture, imshow, imwrite, waitKey, destroyWindow
from huggingface_hub import hf_hub_download
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import preprocess_input
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

#Download model from Hugging Face
model_path = hf_hub_download(
    repo_id="Siddhartha276/Fall_Detection",
    filename="fall_detection_model.h5"
)
#Load the model
model = load_model(model_path)

def ProcessImg(img_path):
    IMG_SIZE = (224, 224)
    img = image.load_img(img_path, target_size=IMG_SIZE)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    plt.imshow(img)
    plt.axis("off")
    plt.show()
    return img_array

def FallDetect(img_array, fallBool):

    prediction = model.predict(img_array)
    print("Raw prediction:", prediction)

    if prediction[0] < 0.60:
        print("Prediction: 🚨 Fall Detected! 🚨")
        fallBool = True
    else:
        print("Prediction: ✅ No Fall Detected.")
        fallBool = False
    return fallBool

def TakeIMG(saveLocation,fileName):

    # Initialize webcam (0 = default camera)
    cam = VideoCapture(0)
    # Capture one frame
    ret, frame = cam.read()

    if ret:
        imwrite(saveLocation+fileName, frame)
        print("Captured image")
    else:
        print("Failed to capture image.")

    cam.release()


def RenameIMG(saveLocation, fallBool):
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y-%H_%M_%S")
    if fallBool == True:
        os.rename(saveLocation+"TEMPNAME.png", saveLocation+"fall_"+dt_string+".png")

    elif fallBool == False:
        os.rename(saveLocation+"TEMPNAME.png", saveLocation+"nofall_"+dt_string+".png")

def DeleteIMG(saveLocation, fileName):
    os.remove(saveLocation+fileName)

