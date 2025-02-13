# Use Ubuntu 22.04 as base image
FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04

# Set non-interactive installation mode to avoid user interaction during build
ENV DEBIAN_FRONTEND=noninteractive

# Add the repository for Python 3.9 and update package lists
RUN apt-get update && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update

# Install Python 3.9 and other necessary packages
RUN apt-get install -y \
    python3.9 \
    python3.9-distutils \
    python3.9-dev \
    python3-pip \
    xvfb \
    xserver-xephyr \
    xserver-xorg \
    libxi-dev \
    libxext-dev \
    ffmpeg \
    git \
    curl \
    vim \
    openjdk-17-jdk \
    tmux \
    unzip \
    curl \
    pciutils \
    && rm -rf /var/lib/apt/lists/*

# Install pip for Python 3.9
RUN python3.9 -m pip install --upgrade pip \
&& python3.9 -m pip install --no-cache-dir setuptools wheel

# Update alternatives to ensure Python 3.9 is the default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1 \
    && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Install pip for Python 3.9
RUN apt-get update && apt-get install -y python3.9-venv python3-pip \
    && python3.9 -m pip install --upgrade pip \
    && python3.9 -m pip install --no-cache-dir setuptools wheel

# Install Node.js and npm from NodeSource
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Install build tools and pkg-config for building native Node.js modules
RUN apt-get update && apt-get install -y build-essential pkg-config libgl1-mesa-dev

# Clone the TeamCraft repository
COPY . /TeamCraft

# Install TeamCraft Python dependencies using Python 3.9
RUN python3.9 -m pip install --no-cache-dir -e /TeamCraft

# Install LLaVA Python dependencies using Python 3.9
RUN python3.9 -m pip install -e /TeamCraft/llava_teamcraft
RUN cd /TeamCraft/llava_teamcraft
RUN python3.9 -m pip install -e "/TeamCraft/llava_teamcraft[train]"
RUN python3.9 -m pip install flash-attn==2.7.3 --no-build-isolation

# Install npm packages and copy necessary files for prismarine-viewer
RUN cd /TeamCraft/teamcraft/env/mineflayer && npm install

# Install the AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws

# Configure the AWS CLI
RUN aws configure set default.s3.max_concurrent_requests 50

# Set the working directory
WORKDIR /TeamCraft

# Command to keep the container running
CMD ["tail", "-f", "/dev/null"]
