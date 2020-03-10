#!/bin/bash

experimentslist=next_experiments.txt

for experiment in $(less $experimentslist)
do
    exp_params=($(echo $experiment | sed "s/,/ /g"))
    echo ${exp_params[@]:1}
    for param in ${exp_params[@]:1}
    do
        echo $(echo $param | sed "s/=/ /g")
        sh changeParam.sh $(echo $param | sed "s/=/ /g")
    done
    file=${exp_params[0]}
    echo Processing $file...
    sh run.sh $file
done