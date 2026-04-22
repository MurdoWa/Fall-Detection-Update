import os.path
from datetime import datetime

#renames image
def RenameIMG(saveLocation, fallpred, threshold):
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y-%H_%M_%S")
    if fallpred < threshold:
        new_name = "fall_" + dt_string + ".png"
        os.rename(saveLocation + "TEMPNAME.png", saveLocation + new_name)
        return new_name

    elif fallpred > threshold:
        new_name = "nofall_" + dt_string + ".png"
        os.rename(saveLocation + "TEMPNAME.png", saveLocation + new_name)
        return new_name
