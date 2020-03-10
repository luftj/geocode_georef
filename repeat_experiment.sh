#!/bin/bash

experiment_number=$1

exp_data=$(cat experiments.csv | grep ^$experiment_number)

input_file=$(echo $exp_data | tr "," "\n" | sed -n 2p)
input_file=$(echo $input_file | cut -c 2- | rev | cut -c 2- | rev) # remove enclosing string delimiters

params=$(echo $exp_data | tr "," "\n" | sed -n 3p | tr " " "\n" | grep =)  # TODO: tr " " invalidates values with spaces, put a proper seperator instead!
params=$(echo $params | cut -c 2- | rev | cut -c 2- | rev) # remove enclosing string delimiters

for param in $params; do
    p=$(echo $param | tr "=" "\n" |  head -1) # parameter name
    v=$(echo $param | tr "=" "\n" |  tail -1) # value # TODO: escape /, they will be misinterpreted by sed
    echo "changing $p to $v"
    bash changeParam.sh $p $v
done

echo "running with $input_file"
bash run.sh $input_file

