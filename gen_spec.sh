#!/bin/bash
sudo rm -rf out
clients=(python typescript rust go)
for client in "${clients[@]}"
do
    sudo docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate \
        -i /local/openapi.json \
        -g $client \
        -o /local/out/$client \
        --package-name trieve_${client}_client
done 
sudo chown -hR $USER:$USER ./out

# update git repositories

mkdir ~/github/
for client in "${clients[@]}"
do
    git clone git@github.com:trieve/trieve_${client}_client.git ~/github/trieve_${client}_client/ # adjust as needed
    cp -r ./out/$client/* ~/github/trieve_${client}_client/
    cd ~/github/trieve_${client}_client/
    git add .
    git commit -m "update $client client"
    git push
done
