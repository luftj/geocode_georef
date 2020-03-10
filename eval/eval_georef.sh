#!/bin/bash

experiment_number=$1

echo "evalutating georef accuracy of experiment no $experiment_number"
# get boundary of warped map
bash eval/raster_footprint.sh $experiment_number

boundary_path=results/$experiment_number/boundary.geojson

# get groundtruth boundary
groundtruth_path=$2

# calculate Jaccard index
touch iou_result
python eval/iou.py $boundary_path $groundtruth_path >> iou_result
value=$(cat iou_result | tail -n 1)
rm iou_result

echo "The warped image matches ground-truth with IoU of $value"
