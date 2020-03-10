#!/bin/python

import argparse
import json

def extract(json, param, value):
    new_feature_list = []
    for idx, feature in enumerate(json["features"]):
        if param in feature["properties"]:
            if str(feature["properties"][param]) == str(value):
                new_feature_list.append(feature)

    json["features"] = new_feature_list
    print(len(json["features"]),"feature with",param,"=",value,"extracted")
    return json


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file path string")
    parser.add_argument("output", help="output file path string")
    parser.add_argument("property", help="property name to look for")
    parser.add_argument("value", help="property value to extract")
    args = parser.parse_args()

    print("extracting features from",args.input)
    jsondata = ""
    with open(args.input) as file:
        jsondata = json.load(file)
        jsondata = extract(jsondata, args.property, args.value)
    
    with open(args.output,"w") as outfile:
        outfile.write(json.dumps(jsondata))