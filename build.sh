#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies for face recognition
apt-get update
apt-get install -y cmake build-essential libboost-all-dev

# Install Python dependencies
pip install -r requirements.txt
