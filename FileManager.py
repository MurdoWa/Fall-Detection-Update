import os.path

def findNextFile(saveLocation):
    files = [f for f in os.listdir(saveLocation) if os.path.isfile(os.path.join(saveLocation, f))]
    numfiles = len(files)
    return numfiles