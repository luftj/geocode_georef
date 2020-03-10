import cv2
import numpy as np
import argparse

import configparser
from simple_cb import simplest_cb

def readParam(param, header):
    config = configparser.ConfigParser()
    config.read("params.config")
    return config[header][param]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file path string")
    parser.add_argument("output", help="output file path string")
    args = parser.parse_args()

    orig = cv2.imread(args.input)
    
    output = simplest_cb(orig, 2)
    black_thresh = 30
    lower = np.array([0,0,0], dtype = "uint8")
    upper = np.array([black_thresh, black_thresh, black_thresh], dtype = "uint8")
 
    # find the colors within the specified boundaries and apply
    # the mask
    sigma = 10
    sharp = cv2.GaussianBlur(output, (5, 5), sigma)
    sharp = cv2.addWeighted(output, 1.5, sharp, -0.5, 0)
    output = cv2.inRange(sharp, lower, upper)
    # output = cv2.morphologyEx(output,cv2.MORPH_ERODE,cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3)))

    # output = cv2.bitwise_not(output)

    kernel = np.zeros((7,3),dtype="uint8")
    kernel[0][1] = 1
    kernel[1][1] = 1
    kernel[2][1] = 1
    kernel[3][1] = 1
    kernel[4][1] = 1
    kernel[5][1] = 1
    kernel[6][1] = 1
    # kernel[7][0] = 1
    # kernel[8][0] = 1
    # output = cv2.filter2D(output,cv2.CV_8U,kernel)
    vertical = cv2.erode(output, kernel)
    vertical = cv2.erode(output, kernel)
    kernel = np.zeros((3,7),dtype="uint8")
    kernel[1][0] = 1
    kernel[1][1] = 1
    kernel[1][2] = 1
    kernel[1][3] = 1
    kernel[1][4] = 1
    kernel[1][5] = 1
    kernel[1][6] = 1
    # kernel[0][7] = 1
    # kernel[0][8] = 1
    horizontal = cv2.erode(output, kernel)

    # output = (output - vertical)

    # kernel = np.zeros((3,3))
    # kernel[1][0] = 0.5
    # kernel[1][1] = 0.5
    # kernel[1][2] = 0.5
    # horizontal = cv2.filter2D(output,cv2.CV_8U,kernel)

    # output = cv2.bitwise_not(output - horizontal)

    lines = vertical + horizontal
    kernel = np.zeros((3,3),dtype="uint8")
    kernel[1][0] = 1
    kernel[1][1] = 1
    kernel[1][2] = 1
    # output -= cv2.morphologyEx(lines,cv2.MORPH_ERODE,kernel)
    kernel = np.zeros((3,3),dtype="uint8")
    kernel[0][1] = 1
    kernel[1][1] = 1
    kernel[2][1] = 1
    # output -= cv2.morphologyEx(lines,cv2.MORPH_ERODE,kernel)
    # output = cv2.bitwise_not(vertical) + cv2.bitwise_not(horizontal)
    # output = cv2.morphologyEx(output,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_RECT,(3,3)))

    output = cv2.bitwise_not(output)
    # output = cv2.cvtColor(output,cv2.COLOR_BGR2GRAY)
    cv2.imwrite(args.output,output)
    sharp = cv2.GaussianBlur(output, (3, 3), 3)
    # preview = cv2.resize(output, (0,0), 0.5, 0.5)
    cv2.imshow("output",output)

    cv2.waitKey()