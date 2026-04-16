import cv2
import time
from huggingface_hub import hf_hub_download
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import preprocess_input
import numpy as np
import matplotlib.pyplot as plt
# Disable ALSA warnings
import ctypes
from ctypes import *
import os
def noalsaerr(*args):
    pass

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
c_error_handler = ERROR_HANDLER_FUNC(noalsaerr)


os.environ["JACK_NO_START_SERVER"] = "1"

#Download model from Hugging Face
model_path = hf_hub_download(
    repo_id="Siddhartha276/Fall_Detection",
    filename="fall_detection_model.h5"
)
#Load the model
model = load_model(model_path)


#sets image to 224x224
#takes in path to image
def ProcessImg(img_path):
    IMG_SIZE = (224, 224)
    img = image.load_img(img_path, target_size=IMG_SIZE)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    #shows image (useless on command line)
    #plt.imshow(img)
    #plt.axis("off")
    #plt.show()
    return img_array

#detects fall
#takes in path to image and fall threshold
#returns prediction as float
def FallDetect(img_array, threshold):

    prediction = model.predict(img_array)
    print("Raw prediction:", prediction)

    if prediction[0] < threshold:
        print("Prediction: 🚨 Fall Detected! 🚨")
    else:
        print("Prediction: ✅ No Fall Detected.")
    return prediction


#takes image
#takes in file save location, name to save the file and the input camera
def TakeIMG(saveLocation, fileName, inputCam):

    cam = cv2.VideoCapture(inputCam)

    # Check if camera opened successfully
    if not cam.isOpened():
        print(f"Camera {inputCam} not available")
        return False

    ret, frame = cam.read()
    if ret:
        cv2.imwrite(saveLocation + fileName, frame)
        print("Captured image")
    else:
        print(f"Failed to capture image from camera {inputCam}")

    cam.release()
    
    # Small pause to reduce Linux V4L2 warnings on repeated access
    time.sleep(0.2)
    
    return ret

def AndResults(analysis1, analysis2 ,threshold):
    if analysis1 > threshold and analysis2 > threshold:
        return True
    else:
        return False
def OrResults(analysis1, analysis2 ,threshold):
    if analysis1 > threshold:
        return True
    elif analysis2 > threshold:
        return True
    else:
        return False

def MeanResults(predictions ):

    analysis3 = np.mean(predictions)
    print(f"{analysis3}")
    return analysis3

