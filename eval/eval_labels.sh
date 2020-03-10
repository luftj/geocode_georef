#!/bin/bash

experiment_number=$1
result_path=results/$experiment_number
label_result=$result_path/strabo/*/final.txt
geocode_result=$result_path/georef/output_gcps.geojson
cluster_result=$result_path/georef/output_refined_gcps.geojson

label_result=$(less $label_result | grep -o coordinates | wc -l)
geocode_result=$(less $geocode_result | grep -o coordinates | wc -l)
cluster_result=$(less $cluster_result | grep -o coordinates | wc -l)

echo "#labels: $label_result"
echo "#after geocode: $geocode_result"
echo "#after clustering: $cluster_result"
