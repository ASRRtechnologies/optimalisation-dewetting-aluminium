import cv2
import numpy as np


class AnalyseImage:
    def __init__(self):
        pass

    img = cv2.imread('images/test-images/test.bmp')
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([50, 50, 50])
    upper = np.array([160, 255, 255])

    mask = cv2.inRange(hsv, lower, upper)

    # Show the image
    cv2.imshow('img', mask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# import path
# path = /Users/lotteboonstra/projects/tud/optimalisation-dewetting-aluminium/images/test-images/Alu_SiC_K_2000.bmp


#
# gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
# gray=cv2.threshold(gray,20,255,cv2.THRESH_BINARY)[1]
# cv2.imshow('gray',gray)
#
# contours,hierarchy = cv2.findContours(gray,cv2.RETR_LIST ,cv2.CHAIN_APPROX_SIMPLE   )
#
# for cnt in contours:
#     area = cv2.contourArea(cnt)
#     if area<400:
#         cv2.drawContours(im,[cnt],0,(255,0,0),2)
#
# cv2.imshow('im',im)
# cv2.waitKey()
