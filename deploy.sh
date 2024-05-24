#!/bin/bash


cd /home/projects/easykart-flask

source .venv/bin/activate

# Clean untracked files and directories
git clean -fd

# Pull the latest changes from the repository
git pull git@github.com:strumberr/easykart-flask-site.git main

# Install any new dependencies
pip3 install -r requirements.txt

sudo systemctl daemon-reload
sudo systemctl start easykart-flask
sudo systemctl status easykart-flask