#!/bin/python

import argparse
import json
from osgeo import ogr

def intersect_json(a, b):
    if len(a["features"]) != 1 or len(b["features"]) != 1:
        raise ValueError("multiple polygons in boundary json!")

    poly_a = ogr.CreateGeometryFromJson(json.dumps(a["features"][0]["geometry"]))
    poly_b = ogr.CreateGeometryFromJson(json.dumps(b["features"][0]["geometry"]))
    intersection_poly = poly_a.Intersection(poly_b)
    area = intersection_poly.GetArea()

    return area

def union_json(a,b):
    if len(a["features"]) != 1 or len(b["features"]) != 1:
        raise ValueError("multiple polygons in boundary json!")

    poly_a = ogr.CreateGeometryFromJson(json.dumps(a["features"][0]["geometry"]))
    poly_b = ogr.CreateGeometryFromJson(json.dumps(b["features"][0]["geometry"]))
    union_poly = poly_a.Union(poly_b)
    area = union_poly.GetArea()

    return area

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("warped", help="result geoJSON poly file path string")
    parser.add_argument("groundtruth", help="ground truth geoJSON poly file path string")
    args = parser.parse_args()

    iou = -1

    with open(args.warped) as result, open(args.groundtruth) as gtruth:
        result_data = json.load(result)
        truth_data = json.load(gtruth)

        intersection = intersect_json(result_data, truth_data)
        union = union_json(result_data, truth_data)
        iou = intersection / union
        # print("I:",intersection)
        # print("U:",union)

    print(iou)