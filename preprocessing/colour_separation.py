# from https://www.curiousily.com/posts/color-palette-extraction-with-k-means-clustering/

from PIL import Image
import random
from math import sqrt

class Point:
    def __init__(self, coordinates):
        self.coordinates = coordinates

class Cluster:
    def __init__(self, center, points):
        self.center = center
        self.points = points

def get_points(image_path):
    img = Image.open(image_path)
    # img.thumbnail((1000,1000)) # todo: does this degrade quality too much?
    img = img.convert("RGB")
    img.show()
    w,h = img.size

    points = []
    for count, colour in img.getcolors(w*h):
        for _ in range(count):
            points.append(Point(colour))

    return points

def euclidean(p, q):
    n_dim = len(p.coordinates)
    return sqrt(sum([
        (p.coordinates[i] - q.coordinates[i]) ** 2 for i in range(n_dim)
    ]))

def distance(p,q):
    return euclidean(p, q) # todo: maybe not the best fot colour differences



class KMeans:
    def __init__(self, n_clusters, min_diff = 1):
        self.n_clusters = n_clusters
        self.min_diff = min_diff

    def assign_points(self, clusters, points):
        plists = [[] for i in range(self.n_clusters)]

        for p in points:
            smallest_distance = float('inf')

            for i in range(self.n_clusters):
                distance = euclidean(p, clusters[i].center)
                if distance < smallest_distance:
                    smallest_distance = distance
                    idx = i

                plists[idx].append(p)

        return plists

    def calculate_center(self, points):
        n_dim = len(points[0].coordinates)
        vals = [0.0 for i in range(n_dim)]
        for p in points:
            for i in range(n_dim):
                vals[i] += p.coordinates[i]
        coords = [(v / len(points)) for v in vals]
        return Point(coords)

    def fit(self, points):
        clusters = [Cluster(center=p, points=[p]) for p in random.sample(points, self.n_clusters)]

        iteration = 0
        while True:
            print("iteration",iteration)
            iteration += 1

            plists = self.assign_points(clusters, points)
            diff = 0

            for i in range(self.n_clusters):
                if not plists[i]:
                    continue
                old = clusters[i]
                center = self.calculate_center(plists[i])
                new = Cluster(center, plists[i])
                clusters[i] = new
                diff = max(diff, euclidean(old.center, new.center))

            if diff < self.min_diff:
                break

        return clusters

def rgb_to_hex(rgb):
    return '#%s' % ''.join(('%02x' % p for p in rgb))

def get_colors(filename, n_colors=3):
    points = get_points(filename)
    clusters = KMeans(n_clusters=n_colors).fit(points)
    clusters.sort(key=lambda c: len(c.points), reverse = True)
    rgbs = [map(int, c.center.coordinates) for c in clusters]
    return list(map(rgb_to_hex, rgbs))
    # return list(rgbs)

def cluster():
    pass


import cv2
from simple_cb import simplest_cb
import numpy as np
import argparse

import configparser

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
    
    img = orig#simplest_cb(orig, 5)

    sigma = 10
    dst	= cv2.bilateralFilter(img, 5, 250, sigma)

    sharp = cv2.GaussianBlur(dst, (5, 5), sigma)
    sharp = cv2.addWeighted(dst, 1.5, sharp, -0.5, 0)

    # cv2.imshow("orig",orig)
    # cv2.imshow("input",img)
    # cv2.imshow("filter",dst)
    # cv2.imshow("sharp",sharp)

    black_thresh = readParam("black_threshold","IMAGEPROC")
    
    lower = np.array([0,0,0], dtype = "uint8")
    upper = np.array([black_thresh, black_thresh, black_thresh], dtype = "uint8")
 
    # find the colors within the specified boundaries and apply
    # the mask
    mask = cv2.inRange(sharp, lower, upper)
    blackhat = cv2.morphologyEx(mask,cv2.MORPH_BLACKHAT,cv2.getStructuringElement(cv2.MORPH_CROSS,(5,5)))
    # blackhat = cv2.bitwise_not(blackhat)
    # cv2.imshow("blackhat",blackhat)
    mask = cv2.bitwise_xor(mask,blackhat)
    kernel = np.ones((3,3),np.uint8)
    mask = cv2.dilate(mask,kernel,iterations = 1)
    # cv2.imshow("mask",mask)
    # Create a blank black image
    white = np.zeros((mask.shape[0], mask.shape[1], 3), np.uint8)
    # Fill image with red color(set each pixel to red)
    white[:] = (255,255,255)
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    inverted = cv2.bitwise_not(sharp)
    # output = cv2.bitwise_and(white, mask_bgr)
    # output = sharp[~np.array(mask)]   
    locs = np.where(mask != 0)
    output = white
    output[locs[0],locs[1]] = sharp[locs[0],locs[1]]
    # output = sharp * (mask[:,:,None].astype(sharp.dtype))
    #output = cv2.bitwise_and(white, inverted, mask = mask)
    # output = cv2.bitwise_not(output)
    output = cv2.cvtColor(output,cv2.COLOR_BGR2GRAY)
    cv2.imwrite(args.output,output)
    # cv2.imshow("output",output)

    # cv2.waitKey()

    # colours = get_colors("ambiguous_topologyx.PNG",6)#
    #colours = get_colors("",2)
    # colours = get_colors("53.png",4)
    # for item in colours:
    #     print(item)
    # print(", ".join(colours))