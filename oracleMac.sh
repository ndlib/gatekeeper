#!/bin/bash

rm -rf lib
mkdir lib

aws s3 sync s3:// lib

pip install cx_oralce -t lib
