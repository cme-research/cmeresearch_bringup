#!/bin/bash

#start brickd
/usr/bin/brickd &

exec "$@"

