#!/bin/bash

# Uncomment the following code and run it seprately to install conda if needed
# then kill current terminal and re-comment following code and run this file

# mkdir -p ~/miniconda3
# wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
# bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
# rm ~/miniconda3/miniconda.sh
# ~/miniconda3/bin/conda init bash

# Make sure activate conda environment before running this script

# conda create -n teamcraft -y python=3.9
# conda activate teamcraft

export DEBIAN_FRONTEND=noninteractive
export NEEDRESTART_SUSPEND=y

sudo apt-get update 
sudo apt-get install -y software-properties-common
# Adding repository for latest Python versions (if needed)
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update

sudo apt-get install -y \
    python3.9 \
    python3.9-distutils \
    python3.9-dev \
    python3-pip \
    xvfb \
    xserver-xorg \
    xserver-xephyr \
    libxi-dev \
    libxext-dev \
    ffmpeg \
    git \
    curl \
    vim \
    openjdk-17-jdk \
    tmux \
    unzip \
    curl 

sudo rm -rf /var/lib/apt/lists/*

# Install pip for Python 3.9
pip install --upgrade pip 
pip install --no-cache-dir setuptools wheel

# Ensure Python 3.9 is the default python3

sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1
sudo update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

sudo apt-get remove python3-apt -y && sudo apt-get install python3-apt

sudo apt-get update 
sudo apt-get install -y python3.9-venv python3-pip
pip install --upgrade pip
pip install --no-cache-dir setuptools wheel

# try sudo apt-get remove python3-apt && sudo apt-get install python3-apt
# if No module named 'apt_pkg' is prompted

# Install Node.js and npm from NodeSource
sudo curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash - && sudo apt-get install -y nodejs


# Install build tools and pkg-config for building native Node.js modules
sudo apt-get update 
sudo apt-get install -y build-essential pkg-config libgl1-mesa-dev


# Install additional depedency
pip install idna certifi psutil

# Install TeamCraft Python dependencies using Python 3.9
echo "Installing TeamCraft"
pip install --no-cache-dir -e .

# Install llava Python dependencies using Python 3.9
echo "Installing llava_teamcraft"
pip install --no-cache-dir -e ./llava_teamcraft/
pip install --no-cache-dir -e ./llava_teamcraft/[train]
pip install flash-attn==2.7.3 --no-build-isolation

# Install npm packages and copy necessary files for prismarine-viewer
cd ./teamcraft/env/mineflayer && npm install

