#!/bin/bash

# Changes parameters for the next experiments
# See params.config for identifiers

if [ "$#" != 2 ];
then
    echo 'please supply a parameter and a new value as arguments'
    echo 'e.g.: changeParam.sh lang eng'
    echo 'string arguments with spaces have to be quoted'
    echo 'e.g.: changeParam.sh transform "order 1"'
    exit
fi

param=$1 # substring of parameter identifier
value=$2 # new value

echo "Changing parameter" $param "to" $value
sed -i "s/$param=.*/$param=$value/" params.config