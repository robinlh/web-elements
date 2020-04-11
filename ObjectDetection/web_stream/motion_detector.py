# import the necessary packages
import numpy as np
import imutils
import cv2


class MotionDetector:
    def __init__(self, accumWeight=0.5):

        # store the accumulated weight factor
        self.accumWeight = accumWeight

        # initialize background model
        self.bg = None

    def update(self, image):

        if self.bg is None:
            self.bg = image.copy().astype("float")
            return

        # update the background model by accumulating the weighted
        # average
        cv2.accumulateWeighted(image, self.bg, self.accumWeight)

    # apply motion detection
    def detect(self, image, tVal=25):
        # abs diff between the background model  and image passed in
        delta = cv2.absdiff(self.bg.astype("uint8"), image)
        thresh = cv2.threshold(delta, tVal, 255, cv2.THRESH_BINARY)[1]

        # blob filtering
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=2)

        # find contours in the thresholded image and init
        # min and max box dims
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        (minX, minY) = (np.inf, np.inf)
        (maxX, maxY) = (-np.inf, -np.inf)

        # if no contours found
        if len(cnts) == 0:
            return None

        for c in cnts:
            # compute bounding box of contour, update min/max
            (x, y, w, h) = cv2.boundingRect(c)
            (minX, minY) = (min(minX, x), min(minY, y))
            (maxX, maxY) = (max(maxX, x + w), max(maxY, y + h))

        # return a tuple of the thresholded image & bounding box dims
        return (thresh, (minX, minY, maxX, maxY))