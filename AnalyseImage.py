import cv2
import cv2.cv2
import numpy as np
import glob
import csv
from datetime import datetime
import os
import errno


def get_value_from_file(path, propertyName):
    t_path = path.replace("tif", "txt")
    print("Retrieving area for picture:", t_path)

    t_values = {}
    with open(t_path) as myfile:
        for line in myfile:
            name, var = line.partition("=")[::2]
            t_values[name.strip()] = var.replace("\n", "")

    return t_values[propertyName]

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
        print("Detected Contour with Area: ", area)

        # minimum area value is to be fixed as the one that leaves the coin as the small object on the scene
        if area > 500:
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


def process_image(path):
    # sourcing the input image
    img = cv2.imread(path)
    imgBlur = cv2.GaussianBlur(img, (3, 3), 0)

    # graying
    imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)

    # Apply threshold - all values below 50 goes to 0, and values above 50 goes to 1.
    ret, thresh_gray = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY)
    # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html
    edges = cv2.Canny(thresh_gray, 50, 150, apertureSize=7)

    kernel = np.ones((2, 2))
    imgDil = cv2.dilate(edges, kernel, iterations=3)
    imgThre = cv2.erode(imgDil, kernel, iterations=3)
    imgFinalContours, finalContours = get_contours(imgThre, img)

    # show  the contours on the unfiltered starting image
    # cv2.imshow("Final External Contours", imgFinalContours)
    # cv2.waitKey()
    cv2.destroyAllWindows()
    return finalContours

class AnalyseImage:
    paths = glob.glob("images/test-images/*.tif")
    print(paths)

    filename = f'output/{datetime.now().date()}/{datetime.now().time()}-output.csv'

    # Create folder if it doesnt exist
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    # open the file in the write mode
    f = open(filename, 'w+')

    # create the csv writer
    writer = csv.writer(f)
    writer.writerow(["ID", "PATH", "PIXEL-AREA", "PIXEL-SIZE", "Area in square nanometers"])

    for path in paths:
        finalContours = process_image(path)
        # write a row to the csv file

        print("Found final contours: ", len(finalContours))
        count = 0

        pixelSize = float(get_value_from_file(path, "PixelSize"))

        for finalContour in finalContours:
            count += 1
            len, area, approx, cnt = finalContour
            print("Appending file with finalContour with area", area)
            writer.writerow([count, path, area, pixelSize, pixelSize * area])

    # close the file
    f.close()


