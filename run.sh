#!/bin/bash

if [ "$#" = 0 ];
then
    echo "please supply a input file as argument"
    exit
fi

inputfile=$1
configfile="params.config"
strabo_config="strabo_configuration.ini"
experiment_number=$(wc -l < experiments.csv)
logfile=logs/log_$experiment_number.txt
touch $logfile
outpath=results/$experiment_number
mkdir $outpath

. ./$configfile # source configuration params



echo "input file:" $inputfile >> $logfile
inputname=$(echo $inputfile | tr "/" "\n" | tail -n 1) # only file name, not path
# inputname=$(echo $inputname | tr "." "\n" | head -n 1) # remove file ending
echo $inputname

if [ "$use_cb" = true ];
then
    echo "starting colour balance"
    echo "using colour balance" >> $logfile
    python preprocessing/simple_cb.py $inputfile $outpath/$inputname $cb_percent >> $logfile
    inputfile=$outpath/$inputname
fi
if [ "$use_colour_sep" = true ];
then
    echo "starting colour separation"
    echo "using colour separation" >> $logfile
    python preprocessing/colour_separation.py $inputfile $outpath/$inputname >> $logfile
    inputfile=$outpath/$inputname
fi

# make sure, we have an alpha channel
# there might not have been one in the input or the colour preprocessing might have stripped
# we need it for calculating the boundary of the final map for evaluation
band=$(gdalinfo $inputfile | grep Band | grep Alpha | awk '{print $2}')
if [ -z "$band" ]
then
    echo "no alpha present, add a channel"
    new_file="${inputfile%.*}.png"
    convert $inputfile -alpha on $new_file
    # overwrite file path variables
    inputfile=$new_file
    echo "new input file:" $inputfile >> $logfile
    inputname=$(echo $inputfile | tr "/" "\n" | tail -n 1) # only file name, not path
    echo $inputname
else
    echo "got alpha in band $band"
fi

echo "starting strabo"
echo "starting strabo" >> $logfile
echo "python strabo-text-recognition-deep-learning/run_command_line.py --image $inputfile --config $strabo_config --checkpoint-path strabo-text-recognition-deep-learning/east_icdar2015_resnet_v1_50_rbox" >> $logfile
python strabo-text-recognition-deep-learning/run_command_line.py --image $inputfile --config $strabo_config --checkpoint-path strabo-text-recognition-deep-learning/east_icdar2015_resnet_v1_50_rbox >> $logfile
strabo_uuid=$(cat $logfile | tail -n 1)
echo "----" $strabo_uuid # UUID for experiment set by strabo
rm lastUID
touch lastUID
echo $strabo_uuid > lastUID

mkdir $outpath/label_samples
mv *.png $outpath/label_samples

mkdir $outpath/strabo
strabo_out=$outpath/strabo/$inputname"_"$strabo_uuid
mv strabo_results/$inputname"_"$strabo_uuid $outpath/strabo/

echo "starting strabo extract py"
echo "python nominatim_localisation/straboExtract.py $strabo_out/final.txt" >> $logfile
python nominatim_localisation/straboExtract.py $strabo_out/final.txt >> $logfile
ocr_output=$(cat $logfile | tail -n 1)

mkdir $outpath/georef
echo "starting localisation py"
echo "python nominatim_localisation/main.py $strabo_out/final.txt $inputfile $outpath/georef/output.tif" >> $logfile
python nominatim_localisation/main.py $strabo_out/final.txt $inputfile $outpath/georef/output.tif  >> $logfile
localised_matches=$(cat $logfile | tail -n 1)

#python3 text_recognition.py -i static/results/test2/TK25_2325_Niendorf_2002.jpg_18e25d96-3b80-11ea-8846-f8b156ff7a22/input.png -j static/results/test2/TK25_2325_Niendorf_2002.jpg_$output/geoJson1.json -o static/results/test2/TK25_2325_Niendorf_2002.jpg_$output/final.txt
#python3 text_recognition.py -i $inputfile -j $strabo_out/geoJson1.json -o $strabo_out/final.txt
# python strabo-text-recognition-deep-learning/run_command_line.py --image $inputfile --config $strabo_config --checkpoint-path strabo-text-recognition-deep-learning/east_icdar2015_resnet_v1_50_rbox

georef_success="false"
if [ -e "$outpath/georef/output.tif" ]
then
    georef_success="true"
    echo "Successfully georeferenced image"
fi

experiment_log=$experiment_number,"\""$inputfile"\"","\""$(cat $configfile)"\"",$strabo_uuid,"\""$ocr_output"\"","\""$localised_matches"\"",$georef_success
echo "$experiment_log"
echo $experiment_log >> experiments.csv
