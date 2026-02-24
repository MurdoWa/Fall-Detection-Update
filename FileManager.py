import os.path
from datetime import datetime

#renames image
def RenameIMG(saveLocation, fallpred, threshold):
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y-%H_%M_%S")
    if fallpred > threshold:
        os.rename(saveLocation+"TEMPNAME.png", saveLocation+"fall_"+dt_string+".png")

    elif fallpred < threshold:
        os.rename(saveLocation+"TEMPNAME.png", saveLocation+"nofall_"+dt_string+".png")

def DeleteIMG(saveLocation, fileName):
    os.remove(saveLocation+fileName)



def findNextFile(saveLocation):
    files = [f for f in os.listdir(saveLocation) if os.path.isfile(os.path.join(saveLocation, f))]
    numfiles = len(files)
    return numfiles