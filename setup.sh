#!/bin/bash

# copy all example files to runable local files to hold secrets
pip install hesburgh-utilities --target hesburgh_pip_install

ln -fs hesburgh_pip_install/hesburgh ./
