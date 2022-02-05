import cv2
import cv2.cv2
import numpy
import numpy as np
import glob
import csv
from datetime import datetime
import os
import errno
import matplotlib.pyplot as plt
import pandas as pd
from numpy import arange
from scipy.optimize import curve_fit


def get_value_from_file(path, propertyName):
    t_path = path.replace("bmp", "txt")
    t_values = {}

    with open(t_path) as myfile:
        for line in myfile:
            name, var = line.partition("=")[::2]
            t_values[name.strip()] = var.replace("\n", "")

    return t_values[propertyName]


def get_density(PixelSize, finalcountours, path):
    dataSize = get_value_from_file(path, "DataSize")
    height, width = dataSize.partition("x")[::2]

    crop = 1200
    # new_height = height - crop
    # new_width = width - crop

    # crop = 1200 * np.ones(len(height))
    # print(len(height))
    # print("this is crop", crop)
    # new_height = np.subtract(height, crop)
    # new_width = np.substract(width, crop)

    # imageArea = int(new_height) * int(new_width) * (PixelSize ** 2)
    # imageArea = (height - crop2) * (width - crop2) * (PixelSize ** 2)
    imageArea = (5120 - crop) * (3840 - crop) * (PixelSize ** 2)
    return imageArea, finalcountours / imageArea


# finding contours
def get_contours(img, imgContour):
    # find all the contours from the B&W image
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # needed to filter only our contours of interest
    final_contours = []

    # for each contour found
    for cnt in contours:
        cv2.drawContours(imgContour, cnt, -1, (255, 0, 255), 2)
        # find its area in pixel
        area = cv2.contourArea(cnt)
        # print("Detected Contour with Area: ", area)

        # minimum area value is to be fixed as the one that leaves the coin as the small object on the scene
        if area > 50:
            perimeter = cv2.arcLength(cnt, True)

            # smaller epsilon -> more vertices detected [= more precision]
            epsilon = 0.002 * perimeter
            # check how many vertices
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            # print(len(approx))

            final_contours.append([len(approx), area, approx, cnt])

    # we want only two objects here: the coin and the meat slice
    print("---\nFinal number of External Contours: ", len(final_contours))
    # so at this point final_contours should have only two elements
    # sorting in ascending order depending on the area
    final_contours = sorted(final_contours, key=lambda x: x[1], reverse=False)

    # drawing contours for the final objects
    for con in final_contours:
        cv2.drawContours(imgContour, con[3], -1, (0, 0, 255), 3)  # color of line contour

    return imgContour, final_contours


def process_image(path, showImages):
    # sourcing the input image
    img = cv2.imread(path)

    crop_img = img[600:3240, 600:4520].copy()

    # blurring
    imgBlur = cv2.GaussianBlur(crop_img, (3, 3), 0)

    # graying
    imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)

    # Apply threshold - all values below 50 goes to 0, and values above 50 goes to 1.
    ret, thresh_gray = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY)
    # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html
    edges = cv2.Canny(thresh_gray, 50, 150, apertureSize=7)

    kernel = np.ones((2, 2))
    imgDil = cv2.dilate(edges, kernel, iterations=3)
    imgThre = cv2.erode(imgDil, kernel, iterations=3)
    imgFinalContours, finalContours = get_contours(imgThre, crop_img)

    # show  the contours on the unfiltered starting image
    if showImages:
        cv2.imshow(path, imgFinalContours)
        cv2.waitKey()
        cv2.destroyAllWindows()

    return finalContours


def get_color(name):
    if name.startswith("Si-NbTiN"):
        return 'k'

    if name.startswith("SiC"):
        return 'b'

    if name.startswith("SiN"):
        return 'y'

    return 'r'


def render_graph(path, output):
    # Initialize the lists for X and Y
    data = pd.read_csv(path)

    df = pd.DataFrame(data)

    X = list(df.iloc[:, 1])
    Y = list(df.iloc[:, 4])

    # Plot the data using bar() method
    plt.bar(X, Y, color='b')
    plt.xticks(rotation=90)
    plt.title("Number of holes per image")
    plt.xlabel("Path title")
    plt.ylabel("Number of holes")
    plt.tight_layout()

    plt.savefig(output)

    # Show the plot
    plt.show()


def render_combinations(baseDir):
    # Initialize the lists for X and Y
    paths = glob.glob(f"{baseDir}/detail/*.csv")
    ax = None
    legend = []

    for path in paths:
        data = pd.read_csv(path)
        prettyName = os.path.basename(path).split(".")[0]
        data.sort_values(["Temperature"])
        df = pd.DataFrame(data)

        x_label = "Temperature"
        y_label = "Density"

        # Plot the data using bar() method
        if ax is not None:
            df.plot(x=x_label, y=y_label, kind="scatter", c=get_color(prettyName), ax=ax)
        else:
            ax = df.plot(x=x_label, y=y_label, kind="scatter", c=get_color(prettyName))

        legend.append(prettyName)
        plt.xticks(rotation=90)
        plt.title(f"Density vs. Temperature {prettyName}")
        plt.xlabel("Temperature (\N{DEGREE SIGN} C)")
        plt.ylabel("Density (holes per squared nanometer)")
        plt.tight_layout()

        plt.savefig(path.replace("csv", "png"))

    ax.legend(legend)
    plt.savefig(f"{baseDir}/summary.png")

    # Show the plot
    plt.show()


class AnalyseImage:
    showImages = True

    paths = glob.glob("images/sanitized/*.bmp")

    baseDir = f"output/{datetime.now().date()}/{datetime.now().time()}"
    summaryFileName = f'{baseDir}/summary.csv'

    # Create folder if it doesnt exisst
    if not os.path.exists(os.path.dirname(summaryFileName)):
        try:
            os.makedirs(os.path.dirname(summaryFileName))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    # open the file in the write mode
    f = open(summaryFileName, 'w+')

    # create the csv writer
    summaryWriter = csv.writer(f)
    summaryWriter.writerow(
        ["Path", "Name", "Image Area", "Pixel Size", "Number of holes", "Total hole size", "Average hole size",
         "Density"])
    imgNo = 0

    for path in paths:
        cf = os.path.basename(path)
        substrate = cf.split("_")[0]
        bilayer = cf.split("_")[1]
        temp = cf.split("_")[2]

        detailBaseDir = f"{baseDir}/detail/"
        os.makedirs(detailBaseDir, exist_ok=True)
        detailPath = f"{detailBaseDir}/{substrate}-{bilayer}.csv"
        exists = os.path.exists(detailPath)
        f2 = open(detailPath, 'a+')
        pathWriter = csv.writer(f2)

        if not exists:
            pathWriter.writerow(
                ["Temperature", "Path", "Number of holes", "Image Area", "Pixel Size", "Cntour Pixel Area",
                 "Area in square nm", "Density"])

        imgNo += 1
        count = 1
        totalArea = 0

        finalContours = process_image(path, showImages)
        pixelSize = float(get_value_from_file(path, "PixelSize"))
        magnification = get_value_from_file(path, "Magnification")
        imageArea, density = get_density(pixelSize, len(finalContours), path)

        for finalContour in finalContours:
            length, area, approx, cnt = finalContour
            totalArea += area
            count += 1

        pathWriter.writerow(
            [temp, path, count, imageArea, pixelSize, totalArea, (pixelSize ** 2) * totalArea, str(density)])
        prettyName = os.path.basename(path).split("_")[0] + "|" + magnification
        summaryWriter.writerow([path, prettyName, imageArea, pixelSize, count, totalArea, totalArea / count, density])

    f.close()
    render_graph(summaryFileName, os.path.dirname(summaryFileName) + "/holes.png")
    render_combinations(baseDir)
