# Flows

Alice connects to a nodered instance to conduct it's command execution.
A user input is parsed, then sent to an LLM instance to be queried.
The Query determines if a flow needs to be run and what the payload should be.
The payload is then sent to the nodered instance to be executed at the flow URL.

This directory contains metadata for the flows that are available to be run.

Basic Flows include:
- [Web Request](web_request.yaml)
- 