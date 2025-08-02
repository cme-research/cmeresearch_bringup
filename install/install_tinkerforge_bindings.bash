#!/bin/bash

wget https://download.tinkerforge.com/apt/$(lsb_release -is | tr [A-Z] [a-z])/archive.key -q -O - | sudo apt-key add -

sudo sh -c "echo 'deb https://download.tinkerforge.com/apt/$(lsb_release -is | tr [A-Z] [a-z]) $(lsb_release -cs) main' > /etc/apt/source"

sudo apt update

sudo apt install python-tinkerforge

# or alternative in raspian

sudo apt install python-pip

pip install tinkerforge

exit 0