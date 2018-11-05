#!/bin/bash

# copy all example files to runable local files to hold secrets
pip install hesburgh-utilities==1.0.9 --target hesburgh_pip_install

ln -fs hesburgh_pip_install/hesburgh ./
