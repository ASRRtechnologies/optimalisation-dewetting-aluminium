import glob
import os



class ImageCleanup:
    print("Initializing helper")
    paths = glob.glob("images/sanitized/*")
    print(len(paths))

    for path in paths:
        fileName = os.path.basename(path)
        bilayer = "none"

        if "TiP-Alu" in fileName:
            bilayer = "TiP-Alu"

        if "TiB-Alu" in fileName:
            bilayer = "TiB-Alu"


        desiredName = fileName.replace("150C", "150")
        desiredName = desiredName.replace("120C", "120")
        desiredName = desiredName.replace("120B", "120")
        desiredName = desiredName.replace("200C", "200")
        desiredName = desiredName.replace("175C", "175")

        # # TiP
        # 120 batch
        desiredName = desiredName.replace("Si-TiP_Alu_11", "Si_TiP-Alu")
        desiredName = desiredName.replace("SiC-TiP_Alu-13", "SiC_TiP-Alu")
        desiredName = desiredName.replace("SiC-TiP_Alu_12", "SiC_TiP-Alu")
        desiredName = desiredName.replace("SiN-TiP_Alu-14", "SiN_TiP-Alu")
        desiredName = desiredName.replace("Si-NbTiN_TiP_Alu-12", "Si-NbTiN_TiP-Alu")
        desiredName = desiredName.replace("Si_NbTiN-TiP_Alu_12", "Si-NbTiN_TiP-Alu")
        desiredName = desiredName.replace("Si-NbT_TiP-Alu", "Si-NbTiN_TiP-Alu")

        #150 batch
        desiredName = desiredName.replace("Si-NbTiN_TiP_Alu-14", "Si-NbTiN_TiP-Alu")
        desiredName = desiredName.replace("Si-TiP_Alu-14", "Si_TiP-Alu")
        desiredName = desiredName.replace("SiC-TiP_Alu-14", "SiC_TiP-Alu")
        desiredName = desiredName.replace("SiN-TiP_Alu-14", "SiN_TiP-Alu")
        desiredName = desiredName.replace("NbT-TiP_Alu-14", "Si-NbTiN_TiP-Alu")

        #170 batch
        desiredName = desiredName.replace("NbTiN-TiP_Alu-12", "Si-NbTiN_TiP-Alu")
        desiredName = desiredName.replace("Si-TiP_Alu-11", "Si_TiP-Alu")
        desiredName = desiredName.replace("SiC-TiP_Alu-13", "SiC_TiP-Alu")
        desiredName = desiredName.replace("SiN-TiP_Alu-14", "SiN_TiP-Alu")

        #200 batch
        desiredName = desiredName.replace("NbT-TiP_Alu-12", "Si-NbTiN_TiP-Alu")
        desiredName = desiredName.replace("Si-TiP_Alu-11", "Si_TiP-Alu")
        desiredName = desiredName.replace("SiC-TiP_Alu-12", "SiC_TiP-Alu")
        desiredName = desiredName.replace("SiN-TiP_Alu-12", "SiN_TiP-Alu")

        if os.path.basename(path) != desiredName:
            print("Renaming ", os.path.basename(path), " to ", desiredName)

        baseDir = f"images/sanitized/{bilayer}"
        os.makedirs(baseDir, exist_ok=True)
        os.rename(path, f"{baseDir}/{desiredName}")