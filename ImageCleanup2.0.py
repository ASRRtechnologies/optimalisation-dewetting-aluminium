import glob
import os

class ImageCleanup2:
    print("Initializing helper")
    paths = glob.glob("images/sanitized/*")
    print(len(paths))

    finalImages = {}

    for path in paths:
        count = 1

        fileName = os.path.basename(path)
        bilayer = "none"
        temp = 0
        substrate = "none"

        if "TiP-Alu" in fileName:
            bilayer = "TiP-Alu"

        if "TiB-Alu" in fileName:
            bilayer = "TiB-Alu"

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
        os.rename(path, f"{baseDir}/{formattedName}_{count}")
    print(finalImages)
