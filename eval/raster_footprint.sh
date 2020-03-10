#!/bin/bash

experiment_number=$1

input_path=results/$experiment_number/georef/output.tif
echo $input_path

# bounding box
# gdaltindex bbox.shp $input_path
# ogr2ogr -f GeoJSON results/$experiment_number/bbox.geojson bbox.shp
# rm bbox.*

# extract exact polygon outline
outpath=results/$experiment_number/boundary.geojson

# get alpha band
band=$(gdalinfo $input_path | grep Band | grep Alpha | awk '{print $2}')

# get all polygons from alpha channel
if [ -n "$band" ]
then
    gdal_polygonize.py $input_path -f GeoJSON polygonised.geojson -b $band
else
    echo "no alpha channel in raster map!"
    exit
fi

# returns UTM, transform to wgs84
ogr2ogr $outpath polygonised.geojson -t_srs epsg:4326

#remove all features with alpha value != 255
python eval/extract_layer.py $outpath $outpath DN 255

# remove temporary file
rm polygonised.geojson

# TODO: simplify output geojson?