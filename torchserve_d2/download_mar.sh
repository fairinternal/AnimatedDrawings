#!/bin/bash

## Create Model Store Directory
echo "Downloading Model Store in: $(pwd)"

## Make Authenticated API Call to S3 Bucket to download mar file
aws s3 cp s3://prod-demo-sketch-in-model-store/D2_humanoid_detector_gpu_half.mar /home/model-server/torchserve_d2/D2_humanoid_detector.mar 
aws s3 cp s3://prod-demo-sketch-in-model-store/res152_256x192.mar /home/model-server/torchserve_d2/res152_256x192.mar
