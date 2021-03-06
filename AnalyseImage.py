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
    imageAreaPixels = (5120 - crop) * (3840 - crop)
    imageArea = imageAreaPixels * (PixelSize ** 2) * 10 ** -6
    return imageArea, finalcountours / imageArea, imageAreaPixels


# finding contours
def get_minimum_area(magnification):
    if magnification < 700:
        return 40

    if 700 <= magnification <= 1300:
        return 150

    return 200


def get_contours(img, imgContour, magnification):
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
        if area > get_minimum_area(int(magnification)):
            perimeter = cv2.arcLength(cnt, True)

            # smaller epsilon -> more vertices detected [= more precision]
            epsilon = 0.002 * perimeter
            # check how many vertices
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            # print(len(approx))

            final_contours.append([len(approx), area, approx, cnt])

    # we want only two objects here: the coin and the meat slice
    print(len(final_contours), end=',')
    # so at this point final_contours should have only two elements
    # sorting in ascending order depending on the area
    final_contours = sorted(final_contours, key=lambda x: x[1], reverse=False)

    # drawing contours for the final objects
    for con in final_contours:
        cv2.drawContours(imgContour, con[3], -1, (0, 0, 255), 3)  # color of line contour

    return imgContour, final_contours


def process_image(path, showImages, magnification):
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
    imgFinalContours, finalContours = get_contours(imgThre, crop_img, magnification)

    # show  the contours on the unfiltered starting image
    if showImages:
        cv2.imshow(path, imgFinalContours)
        cv2.waitKey()
        cv2.destroyAllWindows()

    return finalContours


def get_props_from_path_name(path):
    cf = os.path.basename(path)
    substrate = cf.split("_")[0]
    bilayer = cf.split("_")[1]
    temp = cf.split("_")[2]

    return substrate, bilayer, temp


def get_color(name):
    if name.startswith("Si-NbTiN"):
        return 'k'

    if name.startswith("SiC"):
        return 'b'

    if name.startswith("SiN"):
        return 'y'

    return 'r'


def get_marker(name):
    if name.startswith("Si-NbTiN"):
        return 'o'

    if name.startswith("SiC"):
        return 'v'

    if name.startswith("SiN"):
        return 's'

    return '*'


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


def render_combinations(baseDir, y_label, description, y_min, y_max):
    print(f"Plotting {y_label}")
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

        if ax is not None:
            df.plot(x=x_label, y=y_label, kind="scatter", c=get_color(prettyName), ax=ax, marker=get_marker(prettyName))
        else:
            ax = df.plot(x=x_label, y=y_label, kind="scatter", c=get_color(prettyName), marker=get_marker(prettyName))

        legend.append(prettyName)
        plt.xticks(rotation=90)
        plt.title(f"{y_label} vs. Temperature")
        plt.yscale("log")
        plt.ylim([y_min, y_max])
        plt.xlabel("Temperature (\N{DEGREE SIGN} C)")
        plt.ylabel(f"{y_label} {description}")
        plt.tight_layout()
        plt.grid()

        plt.savefig(path.replace("csv", "png"))

    ax.legend(legend, loc='upper left')
    plt.savefig(f"{baseDir}/{y_label}-summary.png")

    # Show the plot
    plt.show()


class AnalyseImage:
    showImages = False

    globBaseDir = f"output/{datetime.now().date()}/{datetime.now().time()}"

    for bilayer in os.listdir("images/sanitized/"):
        print(f"Executing script for bilayer {bilayer}")

        paths = glob.glob(f"images/sanitized/{bilayer}/*.bmp")
        print(f"Found {len(paths)} images to be analyzed")
        baseDir = f"{globBaseDir}/{bilayer}"
        summaryFileName = f'{baseDir}/summary.csv'

        # Create folder if it doesnt exist
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
             "Density", "Dead Area"])
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
                    ["Temperature", "Path", "Number of holes", "Image Area", "Pixel Size", "Contour Pixel Area",
                     "Area in square nm", "Density", "Average Hole Size", "Magnification", "Dead Area"])

            imgNo += 1
            count = 1
            totalArea = 0
            magnification = get_value_from_file(path, "Magnification")
            finalContours = process_image(path, showImages, magnification)
            pixelSize = float(get_value_from_file(path, "PixelSize"))

            imageArea, density, imageAreaPixels = get_density(pixelSize, len(finalContours), path)

            for finalContour in finalContours:
                length, area, approx, cnt = finalContour
                totalArea += area
                count += 1

            pathWriter.writerow(
                (temp, path, count, imageArea, pixelSize, totalArea, (pixelSize ** 2) * totalArea, str(density),
                 (totalArea * (pixelSize ** 2) * 10 ** -6) / count, magnification, density * 400 * 0.4))
            prettyName = os.path.basename(path).split("_")[0] + "|" + magnification

            summaryWriter.writerow([path,
                                    prettyName,
                                    imageArea,
                                    pixelSize,
                                    count,
                                    totalArea,
                                    ((totalArea * (pixelSize ** 2) * 10 ** -6) / count),
                                    density,
                                    (density * 400 * 0.4)
                                    ])

        print("DONE")
        f.close()
        render_graph(summaryFileName, os.path.dirname(summaryFileName) + "/holes.png")
        render_combinations(baseDir, "Density", " (number of holes per squared micron) ", 10 ** -5, 0.3)
        render_combinations(baseDir, "Average Hole Size", " (squared microns) ", 3 * 10 ** -2, 11)
        render_combinations(baseDir, "Dead Area", " (rate for critically damaging holes in MKID) ", 1 * 10 ** -3, 40)
        print(f"Finished processing {bilayer}")
