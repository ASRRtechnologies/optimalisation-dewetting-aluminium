import glob
import os.path


class helper:
    paths = glob.glob("images/input/*.*")

    for path in paths:
        fileName = os.path.basename(path)
        desiredName = fileName.replace("C", "")
        os.rename(path, os.path.dirname(path) + desiredName)
