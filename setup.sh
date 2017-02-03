#!/bin/bash

# copy all example files to runable local files to hold secrets
ls *Example | sed 's/\(.*\)Example/cp & \1Env/' | sh

echo "Please configure the following files:"
ls *Env | sed

ln -s "/usr/local/lib/python2.7/site-packages/hesburgh"
