#!/bin/bash
apt update && apt upgrade -y && apt autoremove -y
python3 upgrade_pip_all.py
pip3 check
python2 upgrade_pip_all.py
pip2 check
gitup ~
