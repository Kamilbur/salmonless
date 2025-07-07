#!/bin/bash
set -e

INDEX=index_Homo_sapiens.GRCh38

if [ ! -d "$INDEX" ]; then
    echo "There is no index ($INDEX)"
    exit 1
fi

echo "Building base image..."
docker build -t lithops-aws-worker/salmon-base -f Dockerfile.salmon .

echo "Building lithops image..."
lithops runtime build -f Dockerfile.lithops_awslambda -c ../lithops_config_files/aws_lambda.yml -b aws_lambda lithops-aws-worker/salmon
