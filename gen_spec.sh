#!/bin/bash
sudo rm -rf out
sudo docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate \
    -i /local/openapi.json \
    -g python \
    -o /local/out/python \
    --package-name arguflow \

sudo chown -hR $USER:$USER ./out/python
# pip install ./out/python
