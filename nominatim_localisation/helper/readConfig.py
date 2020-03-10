#/usr/bin/python3

import configparser

def readParam(param, header):
    config = configparser.ConfigParser()
    config.read("params.config")
    return config[header][param]