#!/bin/bash
set -e
set -x
sudo apt install -y python-frozendict python-ruamel.yaml
sudo pip install --upgrade --user PyContracts QuickApp conftools comptests procgraph
sudo pip install setuptools wheel
sudo pip install --upgrade ruamel.yaml
