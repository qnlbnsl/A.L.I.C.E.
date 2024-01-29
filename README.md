# Project A.L.I.C.E. Adaptive Life Interpreter and Commmand Executor

This project aims to create an adaptive voice assistant that enables users to execute commands.
Unlike current offerings by big tech, this software is meant to be run locally.

There are multiple parts to this project

1. Mic Array Recorder and streamer.
2. STT Converter
3. Text Analyser and command executor
4. TTS Converter
5. Playback engine.
6. Payload Library

## Mic Array Recorder and streamer

Currently this project runs on a rpi 3b+ with MAtrix Creator. 
It has a 8 microphone array that records audio, then uses webrtc's VAD detection to check for audio. 
Once audio is detected it creates a beamformed audio stream which is streamed to a local server for further analysis

## STT Converter

This portion of the project runs in a GPU backed VM. It uses webrtc to recieve audio and then converts the speech to text. 
It is currently used in conjunction with whisper from openai. Once speech is converted to text, it will then send it over a socket to the Text analyser.

## Text analysis and command executor

This portion gf the project recieves text over websockets. Once recieved, it shall then use a backend to analyse the text for intent or use. 
For this portion we currently use OpenAi's GPT-3.5 model. The model is asked to return a payload that can be easily analyzed. 
After recieving the payload it will then invoke the request commands. These commands must be programmed amnually for now or by using plugins in the future.

## TTS converter. 

Uses a neural TTS engine to convert replies into natural language. Streams audio to an entity with a speaker source. 

## Playback Engine.

Plays recieved audio back tot he user.

## Payload Library

Defines all the communication interfaces used by the project

## NOTES:

There is a bug in av for aiortc where we are unable to install av due to an issue with cython. use the follwing to bypass the issue

PIP_CONSTRAINT=c.txt pip install av==10.0.0

PyPi does not have the latest version of Pyogg. Instead use this:
```sh
pip install git+https://github.com/TeamPyOgg/PyOgg
```

Using LLAMA cpp for python bindings. 
```sh
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
CUDACXX=/usr/local/cuda-12/bin/nvcc CMAKE_ARGS="-DLLAMA_CUBLAS=on -DCMAKE_CUDA_ARCHITECTURES=native" FORCE_CMAKE=1 pip install llama-cpp-python --no-cache-dir --force-reinstall --upgrade
```

For file uploads we use [python-magic](https://pypi.org/project/python-magic/) which requires libmagic. 
```sh
sudo apt-get install libmagic1
```
