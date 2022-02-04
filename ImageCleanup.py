import glob
import os



class ImageCleanup:
    print("Initializing helper")
    paths = glob.glob("images/input/*")
    print(len(paths))

    for path in paths:
        fileName = os.path.basename(path)
        desiredName = fileName.replace("C", "")
        print("Renaming ", path, " to ", desiredName)
        os.rename(path, os.path.dirname(path) + "/" + desiredName)