import requests
import argparse
import os
import json

from helper import readConfig
from straboExtract import handleStraboOut

def geocode_geonames(query):
    countrycode = ""
    if  readConfig.readParam("countrycode","GEOCODING") != "none":
        countrycode += "&country=" + readConfig.readParam("countrycode","GEOCODING")
    url = "http://api.geonames.org/searchJSON?username=jlcsl&inclBbox=true&name=" + query + countrycode

    try:
        r = requests.get(url,headers={'Content-Type': 'application/json'})
        if not r.status_code == 200:
            print("could not get from geonames API")
            print("Error code", r.status_code)
            exit()
    except Exception as e:
        print(e)
        return []

    output = []

    accepted_classes = ["P"]
    # P: city,village,... 
    # A: country, state, region (administrative) 
    # S: spot/building/farm/station
    # L: parks,area,...,
    # H: stream,lake

    for result in r.json()["geonames"]:
        if result["fcl"]in accepted_classes: 
            bbox_size = abs(float(result["bbox"]["east"]) - float(result["bbox"]["west"])) * abs(float(result["bbox"]["north"]) - float(result["bbox"]["south"]))
            entry = "; ".join([result["lat"], result["lng"], str(bbox_size), result["name"], result["adminName1"]])
            output.append(entry)
    return output

def geocode_nominatim(query):
    countrycode = ""
    if  readConfig.readParam("countrycode","GEOCODING") != "none":
        countrycode += "&countrycodes=" + readConfig.readParam("countrycode","GEOCODING")
    url = "https://nominatim.openstreetmap.org/search?format=json&q=" + query + countrycode
    
    try:
        r = requests.get(url,headers={'Content-Type': 'application/json'})
        if not r.status_code == 200:
            print("could not get from osm nominatim")
            print("Error code", r.status_code)
            exit()
    except Exception as e:
        print(e)
        return []

    # print(r.json())
    # print()

    accepted_classes = {"place", "boundary", "landuse"}
    accepted_tyes = {"city", "hamlet", "administrative"}

    output = []

    for result in r.json():
        if result["class"] in accepted_classes:
        #     if result["type"] in accepted_tyes:
                bbox_size = (float(result["boundingbox"][1]) - float(result["boundingbox"][0])) * (float(result["boundingbox"][3]) - float(result["boundingbox"][2]))
                entry = "; ".join([result["lat"], result["lon"], str(bbox_size), result["display_name"]])
                output.append(entry)
    return output

def localise(query, source="osm"):
    if source == "osm":
        return geocode_nominatim(query)
    elif source == "geonames":
        return geocode_geonames(query)
    else:
        raise ValueError("unknown geocoding source requested: " + source)

def georeference(inputfile, outputfile, gcps):
    ''' gcps as [[x,y,lon,lat,name]] '''

    command = "gdal_translate "
    for gcp in gcps:
        command += "-gcp " + " ".join([str(x) for x in gcp[0:4]]) + " "
    # e.g. -gcp 4203.7 2347.0 4.2946 52.0825 
    command += "-of GTiff " + inputfile +  " map-with-gcps.tif"

    os.system(command)

    command = "gdalwarp "
    command += "-"+readConfig.readParam("transform","GEOREF")+" "
    command += "-r bilinear \
        -s_srs \"EPSG:4326\" \
        -t_srs \"EPSG:3857\" \
        -overwrite \
        -tr 20.0 -20.0 \
        map-with-gcps.tif " + outputfile

    print(command)
    os.system(command)

def export_gcps_geojson(gcps, outpath):
    outstring = '{ "type": "FeatureCollection","features": ['
        
    for point in gcps:
        outstring += '{ "type": "Feature","geometry": {"type": "Point", "coordinates": ['
        outstring += point[2] + "," + point[3] # lon, lat
        outstring += ' ]}, "properties": { "text": "'+ point[4] +'" } },'

    outstring = outstring[:-1] # remove trailing comma
    outstring += ' ] }'

    with open(outpath, "w") as file:
        file.write(outstring)

def gcp_distance(P, Q):
    P_lon = float(P[2])
    P_lat = float(P[3])
    Q_lon = float(Q[2])
    Q_lat = float(Q[3])

    distance_squared = abs(P_lon - Q_lon) + abs(P_lat - Q_lat)
    return distance_squared

def range_query(points, Q, eps):
    neighbours = []
    for point in points:
        # TODO: check names, to make sure alternative hyptheses aren't clustered?
        if (point[4] == Q[4]): # compare names
            # neighbour to its own alternative, probably wrong
            continue

        if gcp_distance(point, Q) < eps:
            neighbours.append(point)

    return neighbours

def dbscan(points, eps, minPts):
    num_clusters = 0
    label = [None]*len(points)

    for idx, P in enumerate(points):
        if not label[idx] is None:
            continue # previously processed in inner loop

        neighbours = range_query(points, P, eps) # find neighbours
        if len(neighbours) < minPts: # density check
            label[idx] = -1 # label as noise
            continue

        num_clusters += 1 # next cluster label
        label[idx] = num_clusters # label initial point
        seeds = neighbours # neighbours to expand
        if P in seeds:
            seeds.remove(P)

        for Q in seeds:
            q_idx = points.index(Q) # bad performance? track indizes or labels differently
            if label[q_idx] == -1: # TODO: redundant?
                label[q_idx] = num_clusters # change noise to border point
            if not label[q_idx] is None:
                continue
            label[q_idx] = num_clusters # label neighbour
            q_neighbours = range_query(points, Q, eps) # find neighbours
            if len(q_neighbours) >= minPts: # density check
                seeds += q_neighbours # add new neighbours to seed

    print(list(zip(label,[x[4] for x in points])))

    # find biggest cluster
    clusters = set(label)
    if -1 in clusters:
        clusters.remove(-1) # don't consider noise labels
    if len(clusters) == 0:
        print("no clusters found!")
        return []
    max_c = max(clusters, key=label.count)
    print("biggest cluster", max_c)

    refined_gcps = [p for idx,p in enumerate(points) if label[idx]==max_c ]

    print(refined_gcps)
    return refined_gcps



def cluster_neighbourhood(gcps, map_extent):

    voting_bins = [0]*len(gcps)

    clean_gcps = []

    # test each gcp
    for idx, point in enumerate(gcps):
        lon = float(point[2])
        lat = float(point[3])

        # find neighbours
        for neighbour in gcps:
            if point == neighbour:
                continue
            
            # neighbour_lon = float(neighbour[2])
            # neighbour_lat = float(neighbour[3])

            distance_squared = gcp_distance(point, neighbour)
            # print("dist_sq:",distance_squared)
            
            if distance_squared < map_extent*map_extent:
                # neighbour found

                if (point[4] == neighbour[4]): # compare names
                    # neighbour to its own alternative, probably wrong
                    continue

                voting_bins[idx] += 1

        # TODO: instead, find mean and return all points within map_extent from mean
        print(point[4],"votes:", voting_bins[idx])
        if voting_bins[idx] > 0:
            clean_gcps.append(point)

    return clean_gcps

def remove_duplicate_gcps(gcps):
    already_seen = set()
    ret = []
    for point in gcps:
        if point[4] in already_seen:
            continue # remove duplicate place names
            # TODO: remove all but the one with the highest number of neighbours?
        else:
            already_seen.add(point[4])
            ret.append(point)

    return ret

def refine_gcps(gcps, thresh_lon=0.29, thresh_lat=2.0):
    ''' try to remove outliers from the list of ground control points automatically.
    gcps as [[x,y,lon,lat]] '''

    avg_lon = 0
    avg_lat = 0

    for point in gcps:
        avg_lon += float(point[2])
        avg_lat += float(point[3])

    avg_lon = avg_lon/len(gcps)
    avg_lat = avg_lat/len(gcps)

    ret = []
    for point in gcps:
        diff_lon = abs(float(point[2]) - avg_lon)
        diff_lat = abs(float(point[3]) - avg_lat)
        print("diff",diff_lon,diff_lat)
        if diff_lon > thresh_lon:
            continue
        if diff_lat > thresh_lat:
            continue
        ret.append(point)

    return ret   

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input detection results file path string (final.txt)")
    parser.add_argument("image", help="image file path string (TK25.png)")
    parser.add_argument("output", help="output file path string (output.tif)")
    args = parser.parse_args()

    places = handleStraboOut(args.input)

    gcps = []

    localised_matches = []

    
    already_seen = set()

    for place in places:
        place[0] = ''.join([i for i in place[0] if not i.isdigit()]) # trim numbers from names
        place[0] = place[0].lower() # don't be case-sensitive        
        if len(place[0]) < int(readConfig.readParam("name_minlength","GEOCODING")):
            continue # empty strings or usually partial recognition results
        if place[0] in already_seen:
            continue # remove duplicate place names
        already_seen.add(place[0])
        possible_matches = localise(place[0],source=readConfig.readParam("geocoder_source","GEOCODING"))
        if len(possible_matches) == 0:
            continue # no match
        if len(possible_matches) > int(readConfig.readParam("max_alternatives","GEOCODING")):
            continue # skip general terms. E.g. "Schule", "Platz", ...
        print (place[0], len(possible_matches))
        localised_matches.append(place[0])
        print(possible_matches)

        for match in possible_matches:
            match_info = str.split(match,";")
            gcps.append([place[1][0],place[1][1],match_info[1],match_info[0],place[0]])
            # break # TODO: find a proper way to deal with multiple matches

    print("gcp json out",args.output[:-4]+"_gcps.geojson")
    export_gcps_geojson(gcps,args.output[:-4]+"_gcps.geojson")
    print(len(gcps))
    # TODO: remove duplicate GCPs, i.e. identical x/y or lon/lat
    gcps = dbscan(gcps,float(readConfig.readParam("max_map_extent","GEOREF")),2)
    # gcps = cluster_neighbourhood(gcps, float(readConfig.readParam("max_map_extent","GEOREF")))
    gcps = remove_duplicate_gcps(gcps)
    # gcps = refine_gcps(gcps)
    print(len(gcps))
    export_gcps_geojson(gcps,args.output[:-4]+"_refined_gcps.geojson")

    print(gcps)
    georeference(args.image,args.output,gcps)

    print(localised_matches)