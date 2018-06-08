#!/bin/bash

rm -rf lib
mkdir lib

aws s3 sync s3://libnd-oracle-binary-bucket-oraclebinarybucket-1omf1vksdphrq/oracle_mac lib

pip install cx_oralce -t lib
