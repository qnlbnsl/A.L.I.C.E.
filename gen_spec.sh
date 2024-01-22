#!/bin/bash
sudo rm -rf out
sudo docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate \
    -i /local/openapi.json \
    -g python \
    -o /local/out/python \
    --package-name trieve_python_client \

sudo chown -hR $USER:$USER ./out/python
# pip install ./out/python
