#!/bin/bash

# source /home/model-server/conda/etc/profile.d/conda.sh

# conda activate alphapose

cd /home/ap-server/torchserve_ap

torchserve --start --model-store /home/ap-server/torchserve_ap --models alphapose.mar --ts-config config.properties --log-config log4j.properties --foreground