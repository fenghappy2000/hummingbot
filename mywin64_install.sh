#!/bin/bash

cd $(dirname $0)

#CONDA_EXE=~/miniconda3/Scripts/conda.exe

# Compatibility logic for older Anaconda versions.
if [ "${CONDA_EXE} " == " " ]; then
    CONDA_EXE=$((find /opt/conda/bin/conda || find ~/anaconda3/bin/conda || \
	    find /usr/local/anaconda3/bin/conda || find ~/miniconda3/bin/conda  || \
	    find /root/miniconda/bin/conda || find ~/Anaconda3/Scripts/conda || \
		find ~/miniconda3/Scripts/conda.exe || \
	    find $CONDA/bin/conda) 2>/dev/null)
fi

if [ "${CONDA_EXE}_" == "_" ]; then
    echo "Please install Anaconda w/ Python 3.7+ first"
    echo "See: https://www.anaconda.com/distribution/"
    exit 1
fi

CONDA_BIN=$(dirname ${CONDA_EXE})
MACOS_ENV=setup/environment.yml
LINUX_ENV=setup/environment-linux.yml
LINUX_AARCH64_ENV=setup/environment-linux-aarch64.yml
WIN64_ENV=setup/environment-win64.yml
ENV_FILE=$MACOS_ENV

if uname | egrep -qe "Linux"; then
    if uname -m | egrep -qe "aarch64"; then
        ENV_FILE=$LINUX_AARCH64_ENV
    else
        ENV_FILE=$LINUX_ENV
    fi
elif uname | egrep -qe "MINGW64"; then
    ENV_FILE=$WIN64_ENV
fi

if ${CONDA_EXE} env list | egrep -qe "^hummingbot"; then
    ${CONDA_EXE} env update -f $ENV_FILE
else
    ${CONDA_EXE} env create -f $ENV_FILE
fi

source "${CONDA_BIN}/activate" hummingbot

# Add the project directory to module search paths.
#conda develop .
${CONDA_EXE} develop .

# For some reason, this needs to be installed outside of the environment file,
# or it'll give you the graphviz install error.
${CONDA_BIN}/pip install objgraph

pre-commit install
