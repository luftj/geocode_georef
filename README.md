# Georeferencing by Geocoding
## work in progress

### Description


### Installation

Requires
* python3
* GDAL
  * including gdal_polygonize.py
  * including osgeo python package (windows users might need to install [this](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal) wheel)
* python-opencv
* Strabo

Install Strabo:
1. ```git clone git@github.com:spatial-computing/strabo-text-recognition-deep-learning.git strabo-text-recognition-deep-learning```
2. download install.sh from [here](https://drive.google.com/open?id=17Tat38W_M_4yaHS_dHTf2TakNaT-jQel)
3. download StaboDependancy.zip from [here](https://drive.google.com/file/d/1MjBMO_Ql7kth7VPPX6XkDXW4sr1qtjDV)
4. ```sh install.sh```
5. ```mv east_icdar2015_resnet_v1_50_rbox strabo-text-recognition-deep-learning/east_icdar2015_resnet_v1_50_rbox```

Install this tool:
1. (Optional) set python virtual environment (TODO: install script)
1. ```python -m pip install -r requirements.txt```

ATTENTION: all scripts use the command ```python``` to invoke python3! Your distro might use this command for python2 instead. Python2 might still work but is not tested.

### Usage

```./run.sh <input_image>```

```./run_eperiments.sh``` with experiments to run set in ```next_experiments.txt```

with syntax for ```next_experiments.txt```:

```input file,parameter1=value1,parameter2=value2``` 

Parameter names as in ```params.config```. You can set a input file in every line but only have to provide parameters if you want to change them.

Example: 

```../data/tk25/2000-09/TK25_2426_Wandsbek_2004_cut.jpg,transform=tps,lang=deu,countrycode=DE,psm=7,use_cb=true,use_colour_sep=false```
```../data/tk25/2000-09/TK25_2525_Harburg_2004_cut.jpg```
```../data/tk25/2000-09/TK25_2526_Allermöhe_2004_cut.jpg```

### Evaluation

```./eval/eval_labels.sh <experiment_number>```

This counts the number of text labels detected and left over after geocoding and clusterung respectively.

```./eval/eval_georef.sh <experiment_number> <groundtruth_geojson>```

This calculates the IoU (Intersection over Union) of the resulting warped map image from the experiment number ```<experiment_number>``` with the ground truth polygon given as GeoJSON (use EPSG:4326/WGS84 projection) in ```groundtruth_geojson```.

### Configuration

```params.config```

### Output

All generated output and (intermediary) results will be put in a folder in ```./results/```. The final transformed and warped output geoTIFF will be in ```./results/georef/output.tif```.
Logs will be generated as ```./logs/log_<experiment_number>.txt```.

Additionally, all experiments will be logged with their results and parameters in ```experiments.csv```. DO NOT EDIT THIS FILE. If you remove a line, the last experiment number will be reused and your previous results are replaced.
