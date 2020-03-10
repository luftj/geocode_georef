import json
import argparse

def center_of_bbox(coordinates):
    if len(coordinates) != 5:
        raise ValueError("invalid bbox")

    minx = float("inf")
    miny = float("inf")
    maxx = float("-inf")
    maxy = float("-inf")

    for point in coordinates:
        if point[0] < minx:
            minx = point[0]
        if point[0] > maxx:
            maxx = point[0]
        if point[1] < miny:
            miny = point[1]
        if point[1] > maxy:
            maxy = point[1]

    y = (maxy-miny)/2 + miny
    y = -y # gdal has downward facing y axis!
    return ((maxx-minx)/2 + minx,y)

def handleStraboOut(resultsfile):

    ret = []

    with open(resultsfile) as f:
        data = json.load(f)

        for feature in data["features"]:
            position = center_of_bbox(feature["geometry"]["coordinates"][0])
            name = feature["NameAfterDictionary"]
            if len(name) == 0:
                continue
            entry = [name,position]
            ret.append(entry)

    return ret

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input detection results file path string (final.txt)")
    args = parser.parse_args()

    places = handleStraboOut(args.input)
    print([x[0] for x in places])