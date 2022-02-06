import glob
import os, shutil

class ImageCleanup2:
    print("Initializing helper")
    paths = glob.glob("images/input/*/*/*")
    print(len(paths))

    finalImages = {}

    for path in paths:
        if path.endswith(".tif"):
            os.remove(os.path.join(path))
            continue

        if path.endswith(".txt"):
            continue

        count = 1

        fileName = os.path.basename(path)
        bilayer = "none"
        temp = 0
        substrate = "none"

        if "TiP" in fileName:
            bilayer = "TiP-Alu"

        if "TiB" in fileName:
            bilayer = "TiB-Alu"

        if "RTA" in fileName or "RT" in fileName:
            temp = 21

        if "120" in fileName or "120B" in fileName or "120" in fileName:
            temp = 120

        if "150" in fileName:
            temp = 150

        if "175" in fileName:
            temp = 175

        if "200" in fileName:
            temp = 200

        if "Si-" in fileName or "Si_" in fileName:
            substrate = "Si"

        if "SiC-" in fileName or "SiC_" in fileName:
            substrate = "SiC"

        if "SiN-" in fileName or "SiN_" in fileName:
            substrate = "SiN"

        if "Si-Nb" in fileName or "Si_Nb" in fileName or "NbT" in fileName:
            substrate = "Si-NbTiN"

        formattedName = f"{substrate}_{bilayer}_{temp}"

        if formattedName in finalImages:
            count = finalImages[formattedName] + 1

        finalImages[formattedName] = count

        print(f"Formatted image to {formattedName} with count {count}")

        baseDir = f"images/sanitized/{bilayer}"
        os.makedirs(baseDir, exist_ok=True)
        os.rename(path, f"{baseDir}/{formattedName}_{count}.bmp")
        os.rename(path.replace("bmp", "txt"), f"{baseDir}/{formattedName}_{count}.txt")

    print(finalImages)
    walk = list(os.walk("images/input/"))
    for path, _, _ in walk[::-1]:
        if len(os.listdir(path)) == 0:
            os.rmdir(path)

    os.mkdir("images/input")
