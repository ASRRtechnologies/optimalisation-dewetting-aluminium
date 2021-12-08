import cv2
import numpy as np
import glob
import csv
from datetime import datetime

# finding contours
def get_contours(img, imgContour):
    # find all the contours from the B&W image
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # needed to filter only our contours of interest
    final_contours = []

    # for each contour found
    for cnt in contours:
        # cv2.drawContours(imgContour, cnt, -1, (255, 0, 255), 2)
        # find its area in pixel
        area = cv2.contourArea(cnt)
        print("Detected Contour with Area: ", area)

        # minimum area value is to be fixed as the one that leaves the coin as the small object on the scene
        if (area > 5000):
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
        cv2.drawContours(imgContour, con[3], -1, (0, 0, 255), 3)

    return imgContour, final_contours


def process_image(path):
    # sourcing the input image
    img = cv2.imread(path)
    cv2.imshow("Starting image", img)
    # cv2.waitKey()

    # blurring
    imgBlur = cv2.GaussianBlur(img, (7, 7), 1)
    # graying
    imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)
    # canny
    imgCanny = cv2.Canny(imgGray, 100, 60)  # TODO: figure out correct upper and lower bounds for canny

    kernel = np.ones((2, 2))
    imgDil = cv2.dilate(imgCanny, kernel, iterations=3)
    imgThre = cv2.erode(imgDil, kernel, iterations=3)
    imgFinalContours, finalContours = get_contours(imgThre, img)

    # show  the contours on the unfiltered starting image
    cv2.imshow("Final External Contours", imgFinalContours)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    return len(finalContours)


class AnalyseImage:
    # function that allows multiple files to be read
    # def getImages(self):
    #   for i in

    paths = glob.glob("images/test-images/*.bmp")
    print(paths)

    # open the file in the write mode
    f = open(f'output/{datetime.now()}-output.csv', 'w+')

    # create the csv writer
    writer = csv.writer(f)
    writer.writerow(["PATH", "TOTAL FINAL CONTOURS"])

    for path in paths:
        totalContours = process_image(path)
        # write a row to the csv file
        writer.writerow([path, totalContours])


    # close the file
    f.close()