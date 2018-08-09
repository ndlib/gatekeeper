# Building Oracle Libs

To connect to an oracle DB via python (or node) requires two OS specific libraries.
This document goes over how to build these libraries for a python lambda environment.

There are two main resources required, a python module installed via `pip` and a client library
downloaded from the [oracle website](http://www.oracle.com/technetwork/database/database-technologies/instant-client/overview/index.html)

## Mac
From the root of this directory, run `pip install cx_Oracle -t lib` This should install the python library to the `lib` directory.

To get the client library, go to the the [oracle website](http://www.oracle.com/technetwork/database/database-technologies/instant-client/overview/index.html)
and download the `instantclient-basic` zip. *note, this requires an oracle account* Unzip this into the `lib` directory as well
(flat, so the contents of this zip are not in a subfolder of `lib`).

You should now be able to run queries locally

## Linux (Lambda)
Since the required libraries are OS-specific we need a way to build a Linux version of them, to do this we will use a [docker](https://www.docker.com) container.
We will be using [this repo](https://bitbucket.org/duncan_dickinson/lambda-cx_oracle-public/overview) as a base for building our files.

After downloading the repo, you will need to download the linux RPM versions of the oracle
client from the [oracle website](http://www.oracle.com/technetwork/database/database-technologies/instant-client/overview/index.html)
*note, requires an oracle account* Download the linux x86-64 `instantclient-basic` and `instantclient-devel`
rpms and put them in the `cx-Oracle-packager/rpms` directory of the repo.

You will need to change the files `cx_Oracle-packager/prepare-libs.sh` and `cx_Oracle-packager/Dockerfile`
to reflect the version of the RPM's you downloaded (instructions below).

In `prepare-libs.sh` change the `export LD_LIBRARY_PATH` command to point to the correct version.
The `cp` commands need to be changed pretty drastically, example replacement is below.

```bash
# The cp commands in the repo don't capture everything and some are incorrect.
#  Make sure you copy from the correct version in /usr/lib/oracle/[version]...

# this aio lib is a dependency that's auto-installed, if the version changes this will need to change
cp /lib64/libaio.so.1.0.1 ./lib/
cp ./lib/libaio.so.1.0.1 ./lib/libaio.so.1
cp ./lib/libaio.so.1.0.1 ./lib/libaio.so

cp /usr/lib/oracle/12.1/client64/lib/* ./lib/
rm ./lib/*.jar
rm ./lib/*.zip
chmod 755 ./lib/*.so*

tar cpvzf lib.tar.gz lib
```

In `Dockerfile` change the `yum install` command to point to the rpm file's you put into the `rpms` directory

After making these changes you should be able to run `build.sh` to build the binaries. It will
place the build files in the `dist` folder. To package for labmda, the `dist/lib` folder is the what you need.
Disregard the built zip file, as that includes their test lambda code as well.
